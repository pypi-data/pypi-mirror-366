# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tasks.
"""


class Task:

    def __init__(self, *, innertasks: list[object], is_advanced: bool = False):#TODO list[t.Any]
        self.__innertasks = innertasks
        self.__is_advanced = is_advanced

    @property
    def is_advanced(self) -> bool:
        return self.__is_advanced

    def __call__(self, *args, **kwargs):
        for innertask in self.__innertasks:
            innertask(*args, **kwargs)
