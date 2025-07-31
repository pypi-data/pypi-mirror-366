# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Version control.
"""
import abc
import datetime
import typing as t

import annize.flow.run_context
import annize.data


class VersionControlSystem(abc.ABC):

    @abc.abstractmethod
    def get_current_revision(self) -> str:
        pass

    @abc.abstractmethod
    def get_revision_list(self) -> list[str]:
        pass

    @abc.abstractmethod
    def get_commit_message(self, revision: str) -> str:
        pass

    @abc.abstractmethod
    def get_commit_time(self, revision: str) -> datetime.datetime:
        pass

    @abc.abstractmethod
    def get_revision_number(self, revision: str) -> int:
        pass


class BuildVersion(annize.data.Version):

    def __init__(self, *, base_version: annize.data.Version, vcs: VersionControlSystem):
        super().__init__()
        self.__base_version = base_version
        self.__vcs = vcs

    def __effversion(self):
        # TODO more generic, less weird
        segment_values = {k: v for k, v in self.__base_version.segments_tuples}
        segment_values["build"] = self.__vcs.get_revision_number(self.__vcs.get_current_revision())
        return annize.data.Version(pattern=self.__base_version.pattern, **segment_values)

    @property
    def segments_tuples(self):
        return self.__effversion().segments_tuples

    @property
    def text(self):
        return self.__effversion().text


def default_version_control_system() -> VersionControlSystem|None:
    vcss = annize.flow.run_context.objects_by_type(VersionControlSystem, toplevel_only=True)
    if len(vcss) > 1:
        raise Exception("TODO")
    if len(vcss) == 1:
        return vcss[0]
    return None
