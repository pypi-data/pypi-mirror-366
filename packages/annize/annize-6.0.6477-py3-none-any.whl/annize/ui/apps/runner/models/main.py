# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import datetime
import enum

import klovve.driver

import annize.flow.runner
import annize.i18n
import annize.project.inspector
import annize.project.feature_loader
import annize.project.loader
import annize.ui.apps.runner.models.task_chooser
import annize.ui.apps.runner.models.task_execution
import annize.ui.apps.runner.models.user_feedback


class State(enum.Enum):

    LOADING = enum.auto()
    TASK_CHOOSER = enum.auto()
    TASK_EXECUTION = enum.auto()


class Main(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    def _(self):
        if self.runner and self.run_task:
            self.runner.set_selected_task(self.run_task)
            return annize.ui.apps.runner.models.task_execution.TaskExecution(
                annize_application=self.bind.annize_application,
                runner=self.runner,
                user_feedback=self.user_feedback,
                project_name=annize.i18n.tr("an_UI_pleaseWait"),  # TODO
                task_name=self.run_task,
                status_text=annize.i18n.tr("an_UI_executingSince").format(t=datetime.datetime.now().strftime('%x %X')),
                log_entries=self.bind.log_entries)  # TODO
    current_task_execution: "annize.ui.apps.runner.models.task_execution.TaskExecution|None" = klovve.model.computed_property(_)

    state: State = klovve.model.property(initial=State.LOADING)

    run_task: str|None = klovve.model.property()

    project: "annize.project.Project|None" = klovve.ui.property()

    log_entries: list[klovve.views.LogPager.Entry] = klovve.model.list_property()

    async def _(self):
        if self.project:
            runner = Main._MyRunner(self, project=self.project,
                                    user_feedback_answers=self.annize_application.user_feedback_answers,
                                    user_feedback=self.user_feedback.feedback_controller)
            runner.run_runner()  # TODO  who stops?
            return runner
    runner: "_MyRunner|None" = klovve.model.computed_property(_)

    def _(self):
        if not self.runner:
            return ()
        return self.runner.get_tasks()
    available_tasks: list[str] = klovve.model.computed_property(_)

    def _(self):
        return annize.ui.apps.runner.models.user_feedback.UserFeedback()
    user_feedback: "annize.ui.apps.runner.models.user_feedback.UserFeedback" = klovve.model.computed_property(_)

    def _(self):
        return annize.ui.apps.runner.models.task_chooser.TaskChooser(
            annize_application=self.bind.annize_application,
            available_tasks=self.bind.available_tasks)
    current_task_chooser: "annize.ui.apps.runner.models.task_chooser.TaskChooser" = klovve.model.computed_property(_)

    def _(self):
        if self.runner and self.run_task and self.state != State.TASK_EXECUTION:
            self.runner.set_selected_task(self.run_task)
    fooxx: "TODO" = klovve.model.computed_property(_)  # TODO xx

    def handle_task_chosen(self, task_name: str) -> None:
        self.run_task = task_name

    class _MyRunner(annize.flow.runner.Runner):

        def __init__(self, main: "Main", **kwargs):
            super().__init__(**kwargs)
            self.__main = main

        @klovve.driver.loop.in_driver_loop
        def show_task_chooser(self):
            self.__main.state = State.TASK_CHOOSER

        @klovve.driver.loop.in_driver_loop
        def show_task_execution(self):
            self.__main.state = State.TASK_EXECUTION

        @klovve.driver.loop.in_driver_loop
        def show_task_execution_success(self):
            was_successful, message = self.get_success_state()
            if self.__main.current_task_execution:
                self.__main.current_task_execution.header_style = (
                    klovve.views.HeadBar.Style.SUCCESSFUL if was_successful else klovve.views.HeadBar.Style.FAILED)
                self.__main.current_task_execution.status_text = (
                    annize.i18n.tr("an_UI_successfullyFinishedAt") if was_successful
                    else annize.i18n.tr("an_UI_failedAt")).format(t=datetime.datetime.now().strftime('%x %X'))

            if message:
                self.__main.log_entries.append(klovve.views.LogPager.Entry(
                    message=message,
                    began_at=datetime.datetime.now(),
                    only_single_time=True))
