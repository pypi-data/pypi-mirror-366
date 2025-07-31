# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Changelogs.
"""
import datetime
import typing as t

import annize.flow.run_context
import annize.data
import annize.i18n
import annize.features.version_control.common
import annize.features.version


class Item:

    def __init__(self, *, text: annize.i18n.TrStr):
        self.__text = text

    @property
    def text(self) -> annize.i18n.TrStr:
        return self.__text


class Entry:

    def __init__(self, *, version: annize.data.Version|None, time: datetime.datetime|None,
                 items: t.Iterable[annize.i18n.TrStr|Item]):
        self.__version = version
        self.__time = time
        self.__items = []
        for item in items:
            self.__items.append(item if isinstance(item, Item) else Item(text=item))

    @property
    def items(self) -> list[Item]:
        return self.__items

    @property
    def time(self) -> datetime.datetime|None:
        return self.__time

    @property
    def version(self) -> annize.data.Version|None:
        return self.__version


class Changelog:

    def __init__(self, *, entries: t.Iterable[Entry]):
        self.__entries = list(entries)

    @property
    def entries(self) -> list[Entry]:
        return self.__entries


class ByVersionControlSystemCommitMessagesChangelog(Changelog):  # TODO weg later?!

    def __init__(self):
        super().__init__(entries=())

    _S_CHANGE = "##CHANGE:"
    _S_LABEL = "##LABEL:"

    @property
    def entries(self):
        entries = []
        vcs = annize.features.version_control.common.default_version_control_system()
        if vcs:
            items = []
            for revision in vcs.get_revision_list():
                commitmsg = vcs.get_commit_message(revision)
                for commitmsgline in [x.strip() for x in commitmsg.split("\n")]:
                    if commitmsgline.startswith(self._S_CHANGE):
                        items.append(Item(text=commitmsgline[len(self._S_CHANGE):].strip()))
                    elif commitmsgline.startswith(self._S_LABEL):
                        if len(items) > 0:
                            version = annize.data.Version(text=commitmsgline[len(self._S_LABEL):].strip(),
                                                          pattern=annize.features.version.default_version_pattern())#TODO pattern
                            time = vcs.get_commit_time(revision)
                            entries.append(Entry(version=version, time=time, items=reversed(items)))
                            items = []
        return entries


def default_changelog() -> Changelog:
    prvs = annize.flow.run_context.objects_by_type(Changelog, toplevel_only=True)
    if len(prvs) > 1:
        raise RuntimeError("there is more than one changelog defined in this project")
    if len(prvs) == 1:
        return prvs[0]
    return ByVersionControlSystemCommitMessagesChangelog()
