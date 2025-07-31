# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd
import klovve.variable

import annize.i18n
import annize.project.loader
import annize.ui.apps.studio.models.project_config
import annize.ui.apps.studio.models.problems_list
import annize.ui.apps.studio.models.add_child
import annize.ui.apps.studio.views.add_child


class ObjectEditor(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    project: "annize.project.Project|None" = klovve.ui.property()

    node: "annize.project.Node|None" = klovve.model.property()

    is_expanded: bool = klovve.model.property(initial=False)

    title: str = klovve.model.property(initial="")

    problems_by_node: dict["annize.project.Node", list["annize.ui.apps.studio.models.problems_list.Problem"]] = klovve.ui.property(initial=lambda: {})

    @staticmethod
    def __on_feature_unavailable_node__texts(node: annize.project.OnFeatureUnavailableNode) -> tuple[str, str, str]:
        if node.scope == annize.project.BlockNodeWithScope.Scope.BLOCK:
            where = annize.i18n.tr("an_UI_ofuWithinThisBlock")
        elif node.scope == annize.project.BlockNodeWithScope.Scope.FILE:
            where = annize.i18n.tr("an_UI_ofuWithinThisFile")
        elif node.scope == annize.project.BlockNodeWithScope.Scope.PROJECT:
            where = annize.i18n.tr("an_UI_ofuWithinThisProject")
        else:
            raise Exception("TODO")
        when = annize.i18n.tr("an_UI_ofuWhenFeatureUnavailable").format(f=repr(node.feature))
        if node.do == annize.project.OnFeatureUnavailableNode.Action.SKIP_BLOCK:
            what = annize.i18n.tr("an_UI_ofuDoSkipBlock")
        elif node.do == annize.project.OnFeatureUnavailableNode.Action.SKIP_NODE:
            what = annize.i18n.tr("an_UI_ofuDoSkipNode")
        elif node.do == annize.project.OnFeatureUnavailableNode.Action.FAIL:
            what = annize.i18n.tr("an_UI_ofuDoFail")
        else:
            raise Exception("TODO")
        return where, when, what

    coloration: klovve.views.ObjectEditor.Coloration = klovve.model.property(initial=klovve.views.ObjectEditor.Coloration.GRAY)

    properties: list[tuple[str, list["ObjectEditor"], bool]] = klovve.model.list_property()

    all_actions: list[tuple[str, str, bool]] = klovve.model.list_property()

    _inited: bool = klovve.model.property(initial=False)

    def _(self):
        # TODO xx
        # for BlockNodeWithScope:     self._set_try_hide_argslots(value != annize.project.BlockNodeWithScope.Scope.BLOCK)
        #
        if not self.project:
            return

        with klovve.variable.no_dependency_tracking():
            inited = self._inited
        if self.node and self.annize_application and not inited:
            change_text = f"({annize.i18n.tr('an_UI_change')})"
            with klovve.variable.no_dependency_tracking():
                self._inited = True

            if isinstance(self.node, annize.project.ProjectNode):
                result = annize.i18n.tr("an_UI_projectFiles")
            elif isinstance(self.node, annize.project.FileNode):
                project_path = annize.project.loader.project_root_directory(self.project.annize_config_rootpath)
                node_path = hallyd.fs.Path(self.node.path)
                result = f"{node_path.relative_to(project_path, strict=False)}"
            elif isinstance(self.node, annize.project.ObjectNode):
                result = f"🗂️ {self.node.feature}.{self.node.type_name}"
            elif isinstance(self.node, annize.project.ScalarValueNode):
                result = f" 🔤 {self.node.value!r}"
            elif isinstance(self.node, annize.project.ReferenceNode):
                result = f"🖇️ {annize.i18n.tr('an_UI_referenceTo').format(r=repr(self.node.reference_key))}"
            elif isinstance(self.node, annize.project.OnFeatureUnavailableNode):
                where, when, what = self.__on_feature_unavailable_node__texts(self.node)
                result = f" ✴️ {where}, {when}, {what}"
            else:
                result = "?"
            aux_pieces = []
            if isinstance(self.node, annize.project.ArgumentNode):
                if self.node.name:
                    aux_pieces.append(self.node.name)
                if self.node.append_to:
                    aux_pieces.append(f"⇢{self.node.append_to}")
            if aux := ", ".join(aux_pieces):
                result += f" ({aux})"
            self.title = result

            result = []
            node = self.node
            # TODO clipboard actions?
            result.append((f"*️⃣  {annize.i18n.tr('an_UI_openInNewTab')}", "open_in_new_tab", True))
            if isinstance(node, annize.project.ArgumentNode):
                result.append((f"🏷️ {annize.i18n.tr('an_UI_nameIs').format(n=node.name)} {change_text}"
                               if node.name else f"🏷️ {annize.i18n.tr('an_UI_assignName')}",
                               "change_name", False))
                result.append((f"⇢ {annize.i18n.tr('an_UI_usedAsArgumentFor').format(a=repr(node.append_to))}"
                               if node.append_to else f"⇢ {annize.i18n.tr('an_UI_useAsArgumentFor')}",
                               "change_append_to", not node.append_to))
            if isinstance(node, annize.project.ScalarValueNode):
                result.append((f"🖊️ {annize.i18n.tr('an_UI_setValue')}", "set_value", False))
            if isinstance(node, annize.project.ReferenceNode):
                result.append((f"️⛓️ {annize.i18n.tr('an_UI_setReferenceTarget')}", "set_reference_target", False))
                result.append((f"↕️ {annize.i18n.tr('an_UI_jumpToReferenceTarget')}", "jump_to_reference_target", False))
            if isinstance(node, annize.project.OnFeatureUnavailableNode):
                where, when, what = self.__on_feature_unavailable_node__texts(node)
                result.append((f"🗃️ {where} {change_text}", "change_on_feature_unavailable_node_scope", False))
                result.append((f"⚙️ {when} {change_text}", "change_on_feature_unavailable_node_feature", False))
                result.append((f"🩹 {what} {change_text}", "change_on_feature_unavailable_node_action", False))
            self.all_actions = result

            node_properties = {}
            if not isinstance(self.node, (annize.project.ScalarValueNode,
                                          annize.project.ReferenceNode,
                                          annize.project.OnFeatureUnavailableNode)):
                for matching in self.annize_application.inspector.match_arguments(self.node).all():
                    node_properties[matching.argname] = [], matching.allows_multiple_args or len(matching.nodes) == 0
                    for child_node in matching.nodes:
                        node_properties[matching.argname][0].append(ObjectEditor(
                            annize_application=self.annize_application, node=child_node,
                            problems_by_node=self.bind.problems_by_node,
                            project=self.project))
            self.properties = [(name, children, children_can_be_added_by_user) for name, (children, children_can_be_added_by_user)
                    in node_properties.items()]

            if isinstance(self.node, annize.project.FileNode):
                coloration = klovve.views.ObjectEditor.Coloration.GRAY
            elif isinstance(self.node, annize.project.ObjectNode):
                coloration = klovve.views.ObjectEditor.Coloration.BLUE
            elif isinstance(self.node, annize.project.ScalarValueNode):
                coloration = klovve.views.ObjectEditor.Coloration.GREEN
            elif isinstance(self.node, annize.project.ReferenceNode):
                coloration = klovve.views.ObjectEditor.Coloration.MAGENTA
            elif isinstance(self.node, annize.project.OnFeatureUnavailableNode):
                coloration = klovve.views.ObjectEditor.Coloration.RED
            else:
                coloration = klovve.views.ObjectEditor.Coloration.GRAY
            self.coloration = coloration

            self.node.add_change_handler(self.__handle_node_changed, also_watch_children=False)  # TODO who removes?

    fofhfof = klovve.model.computed_property(_)  # TODO

    def _(self):
        result = []
        has_advanced_actions = False
        for action_title, action_name, action_is_advanced in self.all_actions:
            if action_is_advanced:
                has_advanced_actions = True
            else:
                result.append((action_title, action_name))
        if has_advanced_actions:
            result.append((annize.i18n.tr("an_UI_more"), "show_advanced_actions"))
        return result
    actions: list[tuple[str, str, bool]] = klovve.model.computed_list_property(_)

    def _(self):
        return not isinstance(self.node, annize.project.ProjectNode)
    is_removable_by_user: bool = klovve.model.computed_property(_)

    def _jj(self):
#        return
 #       return print(self.node)
        #return #TODO
        if self.node:
            self.node.add_change_handler(self.__handle_node_changed, also_watch_children=False)
#    foofhf = klovve.model.computed_property(_)  # TODO

    def __handle_node_changed(self, event: annize.project.Node.ChangeEvent) -> None:
#        return print("TODO changed !", self.node, event)
        # TODO
        self.node, node = None, self.node
        self._inited = False
        self.node = node

    async def handle_action_triggered(self, triggering_view: klovve.ui.View, action_name: str) -> None:

        class AdvancedActionsDialog(klovve.ui.dialog.Dialog):

            def __init__(self, actions, **kwargs):
                super().__init__(**kwargs)
                self.__actions = actions

            def view(self):
                return klovve.views.VerticalBox(
                    items=[
                        klovve.views.Button(
                            text=action_title,
                            action_name=action_name,
                            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END),
                            style=klovve.views.Button.Style.LINK)
                        for action_title, action_name in self.__actions])

            @klovve.event.event_handler
            def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent):
                self.close(event.action_name)

        if action_name == "show_advanced_actions":
            advanced_actions = [(action_title, action_name) for action_title, action_name, action_is_advanced
                                in self.all_actions if action_is_advanced]
            if advanced_action_name := await self.annize_application.dialog(
                    AdvancedActionsDialog, (advanced_actions,),
                    is_closable_by_user=True, view_anchor=triggering_view):
                await self.handle_action_triggered(triggering_view, advanced_action_name)
        if action_name == "open_in_new_tab":
            main = self.annize_application.windows[0].body.model  # TODO
            main.project_configs.append(
                annize.ui.apps.studio.models.project_config.ProjectConfig(
                    annize_application=self.bind.annize_application,
                    label=self.bind.title,
                    object_editor=self))
        if action_name == "change_name":
            if (new_node_name := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyNewName").format(t=repr(self.title)),
                    suggestion=self.node.name or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.name = new_node_name or None
                self.__snapshot()
        if action_name == "change_append_to":
            if (new_append_to := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyNameOfObjectWhereToAppendTo").format(t=repr(self.title)),
                    suggestion=self.node.append_to or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.append_to = new_append_to or None
                self.__snapshot()
        if action_name == "set_value":
            if (new_value := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyNewValue"),
                    suggestion=self.node.value or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.value = new_value or None
                self.__snapshot()
        if action_name == "set_reference_target":
            if (new_reference_key := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyReferenceTarget"),
                    suggestion=self.node.reference_key or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.reference_key = new_reference_key or None
                self.__snapshot()
        if action_name == "jump_to_reference_target":
            if reference_target_node := self.annize_application.inspector.resolve_reference_node(self.node):
                self.annize_application.jump_to_node(reference_target_node)
        if action_name == "change_on_feature_unavailable_node_scope":
            if (new_scope := await self.annize_application.dialog(klovve.views.interact.Message(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyOfuScope"),
                    choices=((annize.i18n.tr("an_UI_thisBlock"), annize.project.BlockNodeWithScope.Scope.BLOCK),
                             (annize.i18n.tr("an_UI_thisFile"), annize.project.BlockNodeWithScope.Scope.FILE),
                             (annize.i18n.tr("an_UI_thisProject"), annize.project.BlockNodeWithScope.Scope.PROJECT))),
                    is_closable_by_user=True,
                    view_anchor=triggering_view)) is not None:
                self.node.scope = new_scope
                self.__snapshot()
        if action_name == "change_on_feature_unavailable_node_feature":
            if (new_feature := await self.annize_application.dialog(klovve.views.interact.TextInput(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyOfuFeature"),
                    suggestion=self.node.feature or ""),
                    view_anchor=triggering_view)) is not None:
                self.node.feature = new_feature or ""
                self.__snapshot()
        if action_name == "change_on_feature_unavailable_node_action":
            if (new_do := await self.annize_application.dialog(klovve.views.interact.Message(
                    message=annize.i18n.tr("an_UI_pleaseSpecifyOfuDo"),
                    choices=((annize.i18n.tr("an_UI_doFail"), annize.project.OnFeatureUnavailableNode.Action.FAIL),
                             (annize.i18n.tr("an_UI_doSkipBlock"),
                              annize.project.OnFeatureUnavailableNode.Action.SKIP_BLOCK),
                             (annize.i18n.tr("an_UI_doSkipNode"),
                              annize.project.OnFeatureUnavailableNode.Action.SKIP_NODE))),
                    is_closable_by_user=True,
                    view_anchor=triggering_view)) is not None:
                self.node.do = new_do
                self.__snapshot()

    async def handle_remove_requested(self, triggering_view: klovve.ui.View) -> None:
        if await self.annize_application.dialog(klovve.views.interact.MessageYesNo(
                message=annize.i18n.tr("an_UI_doYouWantToRemove").format(t=repr(self.title))),
                view_anchor=triggering_view):
            self.node.parent.remove_child(self.node)
            self.__snapshot()

    async def handle_add_child_requested(self, triggering_view: klovve.ui.View, property_name: str) -> None:
        suggested_types = self.annize_application.inspector.get_types_for_argument(self.node, property_name)

        if len(suggested_types) == 0:
            newtype = str  # TODO  fail?!
        elif len(suggested_types) == 1:
            newtype = suggested_types[0]
        else:
            child_type_tuples = [(suggested_type.feature, suggested_type.typename, suggested_type) for suggested_type in suggested_types]
            if (child_type_tuple := await self.annize_application.dialog(
                    annize.ui.apps.studio.views.add_child.AddChildDialog,
                    (self.annize_application, child_type_tuples),
                    view_anchor=triggering_view,
                    is_closable_by_user=True)) is None:
                return
            newtype = child_type_tuple[2]

        if newtype.feature:
            newnode = annize.project.ObjectNode()
            newnode.feature = newtype.feature
            newnode.type_name = newtype.typename
        else:
            newnode = annize.project.ScalarValueNode()
            # TODO more?!
        if property_name:
            newnode.arg_name = property_name
        self.node.append_child(newnode)
        self.__snapshot()

    def __snapshot(self):
        # TODO nodesview_controller.snapshot()
        #self.annize_application.has_unsaved_changes = True
        main = self.annize_application.windows[0].body.model  # TODO
        main.snapshot()
