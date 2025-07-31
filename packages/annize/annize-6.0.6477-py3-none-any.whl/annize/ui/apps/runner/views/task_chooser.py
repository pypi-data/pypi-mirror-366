# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.ui.apps.runner.models.task_chooser


class TaskChooser(klovve.ui.ComposedView[annize.ui.apps.runner.models.task_chooser.TaskChooser]):

    def _(self):
        if not self.model:
            return ()

        return [klovve.views.Button(
            text=_,
            action_name=_,
            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.FILL),
            style=klovve.views.Button.Style.FLAT,
            margin=klovve.ui.Margin(vertical_em=0.4, horizontal_em=1)) for _ in self.model.available_tasks]
    task_buttons = klovve.ui.computed_property(_)

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.Label(
                    text=annize.i18n.tr("an_UI_selectTask"),
                    margin=klovve.ui.Margin(horizontal_em=1, vertical_em=1),
                    style=klovve.views.Label.Style.HEADER),
                klovve.views.Scrollable(
                    body=klovve.views.VerticalBox(items=self.bind.task_buttons),
                    vertical_layout=klovve.ui.Layout(min_size_em=12))])

    @klovve.event.event_handler
    def __handle_task_button_clicked(self, event: klovve.app.Application.ActionTriggeredEvent) -> None:
        self.trigger_event(annize.ui.apps.runner.models.task_chooser.TaskChooser.TaskChosenEvent(event.action_name))
        event.stop_processing()
