# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Distributables.

This defines :py:class:`Group` of packages. Package groups can be provided for download on the project homepage or
similar.

There is also :py:class:`PackageStore` for keeping a version history of packages (e.g. somewhere on disk).
"""
import abc
import typing as t

import annize.flow.run_context
import annize.data
import annize.fs
import annize.i18n


class PackageStore(abc.ABC):
    """
    Base class for a package store.
    """

    @abc.abstractmethod
    def store_package(self, items: t.Sequence[annize.fs.FilesystemContent], *, name: str) -> None:
        """
        Store package items.

        :param items: The items to store.
        :param name: The item name.
        """

    @abc.abstractmethod
    def package(self, *, name: str) -> t.Sequence[annize.fs.FilesystemContent]|None:
        """
        Return package items.

        :param name: The item name.
        """

    #TODO weird
    @abc.abstractmethod
    def package_history(self, *, name: str, limit: int = 3) -> t.Sequence[t.Sequence[annize.fs.FilesystemContent]]:
        """
        Return the package history.

        :param name: The item name.
        :param limit: The maximum number of history items to return.
        """


class Group:
    """
    A distributable group of package files.

    Often this contains only a single file, but for some kinds of packages, there can be multiple files related to each
    other somehow.
    """

    def __init__(self, *, title: annize.i18n.TrStr, files: t.Iterable[annize.fs.FilesystemContent],
                 description: annize.i18n.TrStr|None, package_store: PackageStore|None):
        """
        :param title: The title of this group of package files.
        :param files: The package files.
        :param description: Additional description text.
        :param package_store: An optional package store.
        """
        self.__title = title
        self.__files = tuple(files)
        self.__description = description or annize.i18n.to_trstr("")
        self.__package_store = package_store

    @property
    def title(self) -> annize.i18n.TrStr:
        """
        The title of this group of package files.
        """
        return self.__title

    def files(self) -> t.Sequence[annize.fs.FilesystemContent]:
        """
        Return the files of this group.
        """
        try:
            for file in self.__files:
                file.path()
        except Exception:  # TODO  logging
            files_from_package_store = self.__files_from_package_store()
            if files_from_package_store is not None:
                return tuple(files_from_package_store)
            raise
        self.__store_files_to_package_store()
        return self.__files

    @property
    def description(self) -> annize.i18n.TrStr:
        """
        Additional description text.
        """
        return self.__description

    @property
    def package_store(self) -> PackageStore|None:
        """
        An optional package store.
        """
        return self.__package_store

    def __files_from_package_store(self) -> t.Iterable[annize.fs.FilesystemContent]|None:
        if self.__package_store:
            # TODO user interaction
            return self.__package_store.package(name=self.__package_store_name())

    def __store_files_to_package_store(self) -> None:
        if self.__package_store:
            self.__package_store.store_package(self.__files, name=self.__package_store_name())  #TODO pattern=annize.featur.... weg

    def __package_store_name(self) -> str:
        myname = annize.flow.run_context.object_name(self)
        if not annize.flow.run_context.is_friendly_name(myname):
            raise ValueError("a Group must have an object name for package store usage.")
        return myname
