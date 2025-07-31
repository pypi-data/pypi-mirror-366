# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File formats for Annize configuration files.

See also the submodules.
"""
import abc
import os
import typing as t

import hallyd

import annize.project


class FileFormat(abc.ABC):
    """
    A file format for Annize configuration files.
    """

    class Marshaler(abc.ABC):  #TODO baseclass needed?

        @abc.abstractmethod
        def add_change(self, change: "TODO") -> None:  # TODO weg?!
            pass

    @classmethod
    def parse_file(cls, path: hallyd.fs.TInputPath) -> "annize.project.FileNode":
        """
        Read the given file and return a project file node for it.

        :param path: The file to parse.
        """


_formats = {}


def register_file_format(format_name: str):
    def decor(formatclass: type["FileFormat"]):
        _formats[format_name] = formatclass
        return formatclass
    return decor


def get_format(format_name: str) -> "FileFormat|None":
    return _formats.get(format_name)


def parse(path: hallyd.fs.TInputPath) -> "annize.project.ProjectNode":
    import annize.project.file_formats.xml as _  # TODO
    path = str(path)
    path = os.path.abspath(path)
    parent_path, basename = os.path.split(path)
    basename_suffix_idx = basename.rfind(".")
    if basename_suffix_idx > -1:
        files_to_parse = []
        for file_name in os.listdir(parent_path):
            if (file_name.startswith(basename[:basename_suffix_idx + 1])
                    and file_name.endswith(basename[basename_suffix_idx:])):
                files_to_parse.append(f"{parent_path}/{file_name}")
    else:
        files_to_parse = [path]
    project_node = annize.project.ProjectNode()
    for project_file in sorted(files_to_parse):
        parser = get_format("xml")  # TODO
        project_node.append_child(parser.parse_file(project_file))
    return project_node
