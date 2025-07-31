# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio

import klovve

import annize.ui.apps.studio.models.main_tab_panel
import annize.ui.apps.studio.models.project_config
import annize.ui.apps.studio.views.problems_list
import annize.ui.apps.studio.views.project_config


class MainTabPanel(klovve.ui.ComposedView[annize.ui.apps.studio.models.main_tab_panel.MainTabPanel]):

    def compose(self):
        return klovve.views.Tabbed(  # TODO xx select 'All objects' tab at startup - not the Problems tab
            current_tab=self.bind.current_tab,
            tabs=self.bind.tabs)

    def _(self):  # TODO xx odd
        if not self.model:
            return ()
        return self.model.project_configs
    project_configs: list[annize.ui.apps.studio.models.project_config.ProjectConfig] = klovve.ui.computed_list_property(_)

    class __(klovve.model.ListTransformer):
        def output_item(self, item):
            return klovve.views.Tabbed.Tab(
                title=item.bind.shortened_label,
                is_closable=item.bind.is_closable,
                body=annize.ui.apps.studio.views.project_config.ProjectConfig(model=item))
    project_config_tabs: list[klovve.views.Tabbed.Tab] = klovve.ui.transformed_list_property(
        __(), input_list_property=project_configs)

    def _(self):
        if not self.model:
            return ()

        return [
            klovve.views.Tabbed.Tab(
                title=self.model.bind.problems_tab_title,
                body=annize.ui.apps.studio.views.problems_list.ProblemsList(model=self.model.bind.problems_list))]
    additional_tabs: list[klovve.views.Tabbed.Tab] = klovve.ui.computed_list_property(_)

    tabs: list[klovve.views.Tabbed.Tab] = klovve.ui.concatenated_list_property(additional_tabs, project_config_tabs)

    current_tab: klovve.views.Tabbed.Tab|None = klovve.ui.property()

    def _(self):
        if len(self.tabs) >= 2:
            return self.tabs[1]
    main_tab: klovve.views.Tabbed.Tab|None = klovve.ui.computed_property(_)  # TODO

    def _(self):
        if not self.model:
            return

        if jump_to_node := self.model._jump_to_node:
            for tab in [self.current_tab, self.main_tab]:
                if not tab or not isinstance(tab.body, annize.ui.apps.studio.views.project_config.ProjectConfig) or not tab.body.root_object_editor:
                    continue

                object_editors = [(tab.body.root_object_editor,)]
                while object_editors:
                    object_editor_path = object_editors.pop()
                    object_editor = object_editor_path[-1]
                    if object_editor.model.node == jump_to_node:
                        for object_editor_ in object_editor_path:
                            object_editor_.model.is_expanded = True
                        tab.body.object_editor_root.jump_to(object_editor)
                        self.current_tab = tab
                        async def _():
                            await asyncio.sleep(1)  # TODO odd
                            tab.body.object_editor_root.jump_to(object_editor)
                        asyncio.get_running_loop().create_task(_())
                        return
                    for _, object_property_editor in object_editor.properties:
                        for object_editor_children in object_property_editor.children:
                            object_editors.append((*object_editor_path, object_editor_children))

    fooffa = klovve.ui.computed_property(_)  #  TODO
