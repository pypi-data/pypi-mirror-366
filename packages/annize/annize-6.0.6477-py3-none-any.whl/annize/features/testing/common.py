# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Testing.
"""
import abc

import annize.flow.run_context
import annize.data


class RunTests:

    def __init__(self, **b):  # TODO selective (some tests only)
        pass

    def __call__(self, *args, **kwargs):
        for test in annize.flow.run_context.objects_by_type(Test):
            test.run()


class Test(abc.ABC):

    @abc.abstractmethod
    def run(self):
        pass


class TestGroup(Test):

    def __init__(self, *, tests: list[Test]):
        self.__tests = tests

    def run(self):
        for test in self.__tests:
            test.run()
