# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
PyPI store for Python packages.
"""
import subprocess

import annize.fs


class Connection:

    def __init__(self, *, token: str):
        self.__token = token

    @property
    def token(self) -> str:
        return self.__token


class Upload:

    def __init__(self, *, source: annize.fs.FilesystemContent, connection: Connection):
        self.__source = source
        self.__connection = connection

    def __call__(self):
        subprocess.check_call(["twine", "upload", "-u", "__token__", "-p", self.__connection.token,
                               self.__source.path()])
