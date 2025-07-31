# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.ui.apps.runner.models.main
import annize.ui.apps.runner.models.task_chooser
import annize.ui.apps.runner.views.task_chooser
import annize.ui.apps.runner.views.task_execution


class Main(klovve.ui.ComposedView[annize.ui.apps.runner.models.main.Main]):

    def compose(self):
        match self.model.state:
            case annize.ui.apps.runner.models.main.State.LOADING:
                return klovve.views.BusyAnimation()
            case annize.ui.apps.runner.models.main.State.TASK_CHOOSER:
                return annize.ui.apps.runner.views.task_chooser.TaskChooser(
                    model=self.model.bind.current_task_chooser)
            case annize.ui.apps.runner.models.main.State.TASK_EXECUTION:
                return annize.ui.apps.runner.views.task_execution.TaskExecution(
                    model=self.model.bind.current_task_execution)
            case _:
                raise ValueError("invalid state")

    @klovve.event.event_handler
    def __handle_task_chosen(self, event: annize.ui.apps.runner.models.task_chooser.TaskChooser.TaskChosenEvent):
        self.model.handle_task_chosen(event.task_name)
