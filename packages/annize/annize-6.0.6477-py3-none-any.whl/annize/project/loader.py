# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Loading Annize projects from disk.

See also :py:func:`load_project`.
"""
import typing as t

import hallyd

import annize.i18n
import annize.project
import annize.user_feedback


def load_project(project_path: hallyd.fs.TInputPath) -> "annize.project.Project|None":
    """
    Load a project from disk. Return :code:`None` if the given path does not lead to a location inside an Annize
    project.

    Do not use it directly. See :py:meth:`annize.project.Project.load`.

    :param project_path: A path to somewhere inside an Annize project.
    """
    if annize_config_root_file := find_project_annize_config_root_file(project_path):
        return annize.project.Project(annize.project.ProjectNode.load(annize_config_root_file),
                                      annize_config_rootpath=annize_config_root_file)


def find_project_annize_config_root_file(project_path: hallyd.fs.TInputPath) -> hallyd.fs.Path|None:
    """
    Return the main configuration file for an Annize project given by a path (the path may point to somewhere inside
    the project; not only inside the Annize configuration directory), or :code:`None` if the given path does not lead
    to a location inside an Annize project.

    :param project_path: A path into the Annize project.
    """
    currfs = hallyd.fs.Path(project_path)
    if currfs and currfs.is_file():  # TODO noh resolve symlinks?!
        return currfs
    while currfs and currfs.exists():
        for potrespath in ["", *annize_configuration_directory_names]:
            fpotresfs = currfs(potrespath, "project.xml")
            if fpotresfs.is_file():  # TODO noh resolve symlinks?!
                return fpotresfs
        if currfs == currfs.parent:
            break
        currfs = currfs.parent
    return None


def project_root_directory(annize_config_rootpath: hallyd.fs.TInputPath) -> hallyd.fs.Path:
    result = hallyd.fs.Path(annize_config_rootpath).parent
    if result.name in annize_configuration_directory_names:
        result = result.parent
    return result


annize_configuration_directory_names = tuple(f"{prefix}{name}"
                                             for prefix in ("-", ".", "=", "_", "~", "")
                                             for name in ("annize", "meta"))
