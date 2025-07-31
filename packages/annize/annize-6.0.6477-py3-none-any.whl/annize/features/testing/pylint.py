# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
pylint testing.
"""
import subprocess

import annize.features.testing.common
import annize.fs


class Test(annize.features.testing.common.Test):

    def __init__(self, *, source_directory: annize.fs.TInputPath):
        super().__init__()
        self.__source_directory = annize.fs.content(source_directory)

    def run(self):
        src_path = self.__source_directory.path()
        subprocess.check_call(["pylint", src_path], cwd=src_path)
