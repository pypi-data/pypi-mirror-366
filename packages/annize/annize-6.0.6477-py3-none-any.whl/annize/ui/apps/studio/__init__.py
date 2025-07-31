# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import typing as t

import klovve

import annize.i18n
import annize.project.feature_loader
import annize.project.inspector
import annize.project.loader


class Application(klovve.app.Application):

    project: "annize.project.Project" = klovve.ui.property()

    user_feedback_answers: dict[str, t.Any] = klovve.ui.property(initial=lambda: {})

    def _(self):
        return annize.project.feature_loader.DefaultFeatureLoader()  # TODO
    feature_loader: "annize.project.feature_loader.FeatureLoader" = klovve.model.computed_property(_)

    def _(self):
        if not self.feature_loader:
            return None
        return annize.project.inspector.Inspector(self.feature_loader)
    inspector: "annize.project.inspector.Inspector|None" = klovve.model.computed_property(_)

    has_unsaved_changes: bool = klovve.model.property(initial=False)

    def _(self):
        unsaved_text = '(*) ' if self.has_unsaved_changes else ''
        aux_text = f"{unsaved_text}{annize.project.loader.project_root_directory(self.project.annize_config_rootpath)}" if self.project else ""
        return f"{f'{aux_text} - ' if aux_text else ''}Annize"
    window_title: str = klovve.model.computed_property(_)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from annize.ui.apps.studio.models.main import Main as MainModel
        from annize.ui.apps.studio.views.main import Main as MainView

        self.windows.append(klovve.views.Window(
            title=self.bind.window_title,
            body=MainView(
                model=MainModel(
                    annize_application=self,
                    has_unsaved_changes=self.bind.has_unsaved_changes,
                    project=self.bind.project))))

    def jump_to_node(self, node: "annize.project.Node") -> None:
        self.windows[0].body.model.main_tab_panel.jump_to_node(node)

    @klovve.event.event_handler
    def __handle_window_close_requested(self, event: klovve.views.Window.CloseRequestedEvent) -> None:
        event.stop_processing()
        asyncio.get_running_loop().create_task(self.__handle_window_close_requested__async(event.window))

    async def __handle_window_close_requested__async(self, window: klovve.views.Window) -> None:
        if self.has_unsaved_changes:
            action = await self.dialog(klovve.views.interact.Message(
                message=annize.i18n.tr("an_UI_thereAreUnsavedChangesHowToProceed"),
                choices=(
                    (annize.i18n.tr("an_UI_saveAndClose"), "save"),
                    (annize.i18n.tr("an_UI_closeWithoutSaving"), None),
                    (annize.i18n.tr("an_UI_cancel"), "cancel"))),
                view_anchor=window)
            if action == "cancel":
                return
            if action == "save":
                self.project.save()

        window.close()
