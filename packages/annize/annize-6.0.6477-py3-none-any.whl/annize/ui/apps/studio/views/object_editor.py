# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio

import klovve

import annize.ui.apps.studio.models.object_editor
import annize.ui.apps.studio.models.problems_list


class ObjectEditor(klovve.ui.ComposedView[annize.ui.apps.studio.models.object_editor.ObjectEditor]):

    def compose(self):
        return klovve.views.ObjectEditor(
            title=self.model.bind.title,
            coloration=self.model.bind.coloration,
            properties=self.bind.properties,
            additional_views=self.bind.additional_views,
            is_expanded=self.model.bind.is_expanded,
            is_removable_by_user=self.model.bind.is_removable_by_user,
            actions=self.model.bind.actions)

    def _(self):
        if not self.model:
            return ()
        result = []
        for problem in self.model.problems_by_node.get(self.model.node) or ():
            severity_str = {
                annize.ui.apps.studio.models.problems_list.Severity.WARNING: "⚠️",
                annize.ui.apps.studio.models.problems_list.Severity.ERROR: "⛔️"}[problem.severity]
            severity_label_style = {
                annize.ui.apps.studio.models.problems_list.Severity.WARNING: klovve.views.Label.Style.WARNING,
                annize.ui.apps.studio.models.problems_list.Severity.ERROR: klovve.views.Label.Style.ERROR
            }[problem.severity]
            result.append(klovve.views.Label(text=f"{severity_str} {problem.text}", style=severity_label_style))
        return result
    additional_views: list[klovve.ui.View] = klovve.ui.computed_list_property(_)

    def _(self):
        if not self.model:
            return []
        return [(property_name, klovve.views.ObjectPropertyEditor(
                    children=[ObjectEditor(model=model) for model in child_object_editor_models],
                    children_can_be_added_by_user=children_can_be_added_by_user))
                for property_name, child_object_editor_models, children_can_be_added_by_user in self.model.properties]
    properties = klovve.ui.computed_list_property(_)

    def _(self):  # TODO (needed e.g. for the location bar)
        if not self.model:
            return False
        return self.model.is_expanded
    is_expanded = klovve.ui.computed_property(_)

    def _(self):  # TODO (needed e.g. for the location bar)
        if not self.model:
            return ""
        return self.model.title
    title = klovve.ui.computed_property(_)

    @klovve.event.event_handler
    def __handle_action_triggered(self, event: klovve.views.ObjectEditor.ActionTriggeredEvent) -> None:
        event.stop_processing()
        asyncio.get_running_loop().create_task(
            self.model.handle_action_triggered(event.triggering_view, event.action_name))

    @klovve.event.event_handler
    def __handle_remove_requested(self, event: klovve.views.ObjectEditor.RemoveRequestedEvent) -> None:
        event.stop_processing()
        asyncio.get_running_loop().create_task(self.model.handle_remove_requested(self))

    @klovve.event.event_handler
    def __handle_add_child_requested(self, event: klovve.views.ObjectPropertyEditor.AddChildRequestedEvent) -> None:
        event.stop_processing()
        for property_name, object_property_editor in self.properties:
            if object_property_editor is event.object_property_editor:
                asyncio.get_running_loop().create_task(self.model.handle_add_child_requested(self, property_name))
                break
