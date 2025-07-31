# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import subprocess

import klovve

import annize.asset
import annize.i18n
import annize.ui.apps.studio.models.main
import annize.ui.apps.studio.views.main_tab_panel


class Main(klovve.ui.ComposedView[annize.ui.apps.studio.models.main.Main]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.HeadBar(
                    primary_header_views=[
                        klovve.views.Button(text="☰", action_name="show_menu", style=klovve.views.Button.Style.FLAT),
                        klovve.views.Button(text="▸", action_name="run_project", style=klovve.views.Button.Style.FLAT,
                                            is_enabled=self.model.bind.can_run),
                        klovve.views.Label(text="|", style=klovve.views.Label.Style.HIGHLIGHTED),
                        klovve.views.Button(text=annize.i18n.tr("an_UI_undo"), action_name="undo",
                                            style=klovve.views.Button.Style.FLAT,
                                            is_enabled=self.model.bind.can_undo_change),
                        klovve.views.Button(text=annize.i18n.tr("an_UI_redo"), action_name="redo",
                                            style=klovve.views.Button.Style.FLAT,
                                            is_enabled=self.model.bind.can_redo_change),
                    ],
                    secondary_header_views=[
                        klovve.views.Button(text="❓", action_name="help", style=klovve.views.Button.Style.FLAT)
                    ]),
                klovve.views.Placeholder(body=self.bind.main_body)],
            vertical_layout=klovve.ui.Layout(min_size_em=16),
            horizontal_layout=klovve.ui.Layout(min_size_em=20))

    def _(self):
        if not self.model:
            return klovve.views.Label()
        if self.model.project:
            return annize.ui.apps.studio.views.main_tab_panel.MainTabPanel(model=self.model.bind.main_tab_panel)
        else:
            return klovve.views.Label(text=annize.i18n.tr("an_UI_nextOpenOrCreateProject"),
                                      style=klovve.views.Label.Style.HIGHLIGHTED)
    main_body: klovve.ui.View = klovve.ui.computed_property(_)

    @klovve.event.event_handler
    def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent) -> None:
        event.stop_processing()
        asyncio.get_running_loop().create_task(self.__handle_action_triggered__async(event))

    async def __handle_action_triggered__async(self, event: klovve.app.Application.ActionTriggeredEvent) -> None:
        class AdvancedActionsDialog(klovve.ui.dialog.Dialog):  # TODO dedup (add sth to klovve?!)

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

        if event.action_name == "show_menu":
            menu_actions = ((annize.i18n.tr("an_UI_createProject"), "create_project"),
                            (annize.i18n.tr("an_UI_openAnotherProject") if self.model.project else
                             annize.i18n.tr("an_UI_openProject"), "open_project"),
                            *(((annize.i18n.tr("an_UI_saveProject"), "save_project"),)
                              if self.model.has_unsaved_changes else ()))
            if (action := await self.application.dialog(AdvancedActionsDialog, (menu_actions,),
                                                        view_anchor=event.triggering_view,
                                                        is_closable_by_user=True)):
                if action == "save_project":
                    self.model.save_changes()
                elif action == "create_project" or action == "open_project":
                    dialog_title = (annize.i18n.tr("an_UI_chooseProjectRootDirectory")
                                    if action == "create_project" else annize.i18n.tr("an_UI_openProject"))
                    if (project_dir := await self.application.dialog(klovve.ui.dialog.Filesystem.OpenDirectoryDialog,
                                                                     view_anchor=event.triggering_view,
                                                                     title=dialog_title,
                                                                     is_closable_by_user=True)):
                        is_valid_project_dir = self.model.is_valid_project_dir(project_dir)
                        if is_valid_project_dir or action == "create_project" or await self.application.dialog(
                                klovve.views.interact.MessageYesNo(
                                    message=f"This is not a directory inside an Annize project.\n\n"
                                            f"Do you want to create a new project in {str(project_dir)!r}?"),
                                view_anchor=event.triggering_view):
                            self.model.create_or_load_project(project_dir)
        elif event.action_name == "run_project":
            #TODO xx  this does not apply the latest (unsaved) changes; but would not even apply the saved ones!
            with annize.ui.app(
                    "runner", project=self.model.project,
                    user_feedback_answers=self.model.annize_application.user_feedback_answers) as (app, app_ctrl):
                app_ctrl.start()
        elif event.action_name == "undo":
            self.model.undo_change()
        elif event.action_name == "redo":
            self.model.redo_change()
        elif event.action_name == "help":
            menu_actions = ((annize.i18n.tr("an_UI_documentation"), "documentation"),
                            (annize.i18n.tr("an_UI_about"), "about"))
            if (action := await self.application.dialog(AdvancedActionsDialog, (menu_actions,),
                                                        view_anchor=event.triggering_view,
                                                        is_closable_by_user=True)) is not None:
                if action == "documentation":
                    subprocess.Popen(["xdg-open", annize.asset.data.readme_pdf(annize.i18n.current_culture().iso_639_1_language_code)])
                elif action == "about":
                    print("TODO about")


"""
TODO
- make the visualization of the project node "lighter". e.g. no title, no frame, no property guide lines
- fix some display issues: why are inner object editors not horizontally expanding? what happens to the delete button?
- documentation/about
- jump to the right tab on startup resp. after a project is loaded
- jump to append_to source (and have a reference nodebox for it with reduced functionality)
- object editor: try to hide nameless property slot sometimes?
- clipboard actions / dnd?
- add/remove files ; add/remove other special nodes, e.g. on-feature-unavailable nodes
- change order of nodes in an argslot (also possible by keyboard/touch)
- "project.xml" should be the first file shown
"""
