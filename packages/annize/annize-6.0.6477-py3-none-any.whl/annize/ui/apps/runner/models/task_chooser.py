# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class TaskChooser(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    available_tasks: list[str] = klovve.model.list_property()

    class TaskChosenEvent(klovve.event.Event):

        def __init__(self, task_name: str):
            super().__init__()
            self.__task_name = task_name

        @property
        def task_name(self) -> str:
            return self.__task_name
