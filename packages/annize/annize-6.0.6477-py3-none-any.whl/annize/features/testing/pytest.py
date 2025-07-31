# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
pytest testing.
"""
import os
import subprocess

import annize.features.base
import annize.features.testing.common
import annize.fs


class Test(annize.features.testing.common.Test):

    def __init__(self, *, test_directory: annize.fs.TInputPath, source_directory: annize.fs.TInputPath):
        super().__init__()
        self.__source_directory = annize.fs.content(source_directory)
        self.__test_directory = annize.fs.content(test_directory)

    def run(self):
        source_directory = self.__source_directory.path()
        test_directory = self.__test_directory.path()
        # TODO zz
        os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + f":{test_directory}"
        # TODO zz see the mess in anise4
        subprocess.check_call(["pytest", test_directory], cwd=source_directory)
