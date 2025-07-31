# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Injections.
"""
import abc

import annize.fs
import annize.features.base


class Injection(abc.ABC):

    @abc.abstractmethod
    def inject(self, destination: annize.fs.Path):
        pass


class FilesystemContentInjection(Injection):

    def __init__(self, *, content: annize.fs.TFilesystemContent):
        super().__init__()
        self.__content = annize.fs.content(content)

    @property
    def content(self) -> annize.fs.FilesystemContent:
        return self.__content

    def inject(self, destination: annize.fs.Path):
        self.__content.path().copy_to(destination, destination_as_parent=True, overwrite=True)


class Inject:

    def __init__(self, *, injection: Injection, destination: annize.fs.Path):
        self.__injection = injection
        self.__destination = destination

    def __call__(self):
        self.__injection.inject(annize.features.base.project_directory()(self.__destination))
