# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The Annize project runner.

See :py:class:`Runner`.
"""
import abc
import threading
import traceback
import typing as t

import annize.flow.run_context
import annize.i18n
import annize.project.loader
import annize.project.materializer
import annize.user_feedback.static


class Runner(abc.ABC):
    """
    TODO.
    """

    def __init__(self, *, project: annize.project.Project, selected_task: str|None = None,
                 user_feedback_answers: dict[str, t.Any],
                 user_feedback: "TODO" = None):
        self.__project = project
        self.__tasks = None
        self.__selected_task = selected_task or None
        self.__user_feedback_answers = user_feedback_answers
        self.__user_feedback = user_feedback
        self.__success_state = None
        self.__lock = threading.Lock()
        self.__condition = threading.Condition(self.__lock)

    def run_runner(self) -> None:
        threading.Thread(target=self.__do_run, args=(self.__project,), daemon=True).start()

    def _dispatch(self, func):
        with annize.i18n.annize_user_interaction_culture:  # TODO ?!?! (we already have that somewhere else?!)
            func()

    def __do_run(self, project: annize.project.Project):
        tasks = []
        taskobjs = {}
        context = annize.flow.run_context.RunContext()
        context.prepare(annize_config_rootpath=project.annize_config_rootpath)
        with context as ctx:
            annize.user_feedback._add_controller_to_context(
                controller=annize.user_feedback.static.StaticUserFeedbackController(self.__user_feedback_answers),
                context=context, priority_index=100_000)
            if self.__user_feedback:
                annize.user_feedback._add_controller_to_context(controller=self.__user_feedback, context=ctx,
                                                                priority_index=-100_000)

            with annize.i18n.annize_user_interaction_culture:  # TODO ?!?! (we already have that somewhere else?!)
                annize.project.materializer.materialize(project.node)
                for obj in ctx.objects_by_type(object):
                    objname = context.object_name(obj)
                    if context.is_friendly_name(objname):
                        if callable(obj):
                            tasks.append(objname)
                            taskobjs[objname] = obj
                self.__set_tasks(tasks)
                if self.__selected_task is None:
                    self._dispatch(self.show_task_chooser)
                    with self.__lock:
                        while self.__selected_task is None:
                            self.__condition.wait()
                if self.__selected_task:
                    task = taskobjs[self.__selected_task]
                    self._dispatch(self.show_task_execution)
                    try:
                        task()
                        self.__set_success_state(True, "")
                    except Exception:
                        self.__set_success_state(False, f"\nFailed:\n{traceback.format_exc()}\n")
                else:
                    self.__set_success_state(False, f"\nCancelled.\n")
                self._dispatch(self.show_task_execution_success)

    @abc.abstractmethod
    def show_task_chooser(self) -> None:
        pass

    @abc.abstractmethod
    def show_task_execution(self) -> None:
        pass

    @abc.abstractmethod
    def show_task_execution_success(self) -> None:
        pass

    def get_tasks(self) -> list[str]:
        with self.__lock:
            while self.__tasks is None:
                self.__condition.wait()
            return self.__tasks

    def __set_tasks(self, tasks: list[str]) -> None:
        with self.__lock:
            self.__tasks = tasks
            self.__condition.notify_all()

    def get_selected_task(self) -> str:
        with self.__lock:
            while self.__selected_task is None:
                self.__condition.wait()
            return self.__selected_task

    def set_selected_task(self, task_name: str) -> None:
        with self.__lock:
            self.__selected_task = task_name or ""
            self.__condition.notify()

    def is_finished(self) -> bool:
        with self.__lock:
            return self.__success_state is not None

    def get_success_state(self) -> t.Tuple[bool, str]:
        with self.__lock:
            while self.__success_state is None:
                self.__condition.wait()
            return self.__success_state

    def __set_success_state(self, success: bool, message: str) -> None:
        with self.__lock:
            self.__success_state = success, message
            self.__condition.notify_all()

    def wait_finished(self) -> None:
        self.get_success_state()
