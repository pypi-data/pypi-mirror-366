# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Python injections.
"""
import typing as t

import annize.data
import annize.features.base
import annize.features.injections.common
import annize.fs


class ProjectInfoInjection(annize.features.injections.common.Injection):

    def __init__(self, *, filename: str = "project_info.py", version: annize.data.Version|None):
        super().__init__()
        self.__filename = filename
        self.__version = version

    def inject(self, destination: annize.fs.Path):
        pieces = [
            ("homepage_url", annize.features.base.homepage_url()),
            ("version", str(self.__version))
        ]
        content = ""
        for piecekey, piecevalue in pieces:
            if piecevalue is not None:
                content += f"{piecekey} = {repr(piecevalue)}\n"
        destination(self.__filename).write_file(content)
