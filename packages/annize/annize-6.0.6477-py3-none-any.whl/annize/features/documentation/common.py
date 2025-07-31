# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Documentation.
"""
import abc
import typing as t

import annize.fs
import annize.i18n


class DocumentGenerateResult:

    def __init__(self, file: annize.fs.FilesystemContent, entry_path: str):
        self.__file = file
        self.__entry_path = entry_path

    @property
    def file(self) -> annize.fs.FilesystemContent:
        return self.__file

    @property
    def entry_path(self) -> str:
        return self.__entry_path

    def _set_entry_path(self, entry_path: str) -> None:
        self.__entry_path = entry_path


class DocumentGenerateAllCulturesResult(DocumentGenerateResult):

    def __init__(self, file: annize.fs.FilesystemContent, entry_path: str, entry_paths_for_languages: dict[str, str]):
        super().__init__(file, entry_path)
        self.__entrypathsforlanguages = entry_paths_for_languages

    def entry_path_for_language(self, language: str) -> str:
        return self.__entrypathsforlanguages[language]

    @property
    def culture_names(self) -> t.Sequence[str]:
        return tuple(self.__entrypathsforlanguages.keys())


class Document(abc.ABC):

    @abc.abstractmethod
    def available_cultures(self) -> t.Sequence[annize.i18n.Culture]:
        pass

    @abc.abstractmethod
    def generate(self, output_spec, *,
                 culture: annize.i18n.Culture = annize.i18n.unspecified_culture) -> DocumentGenerateResult:
        pass

    @abc.abstractmethod
    def generate_all_cultures(self, output_spec) -> DocumentGenerateAllCulturesResult:
        pass


class OutputSpec(abc.ABC):
    """
    Base class for documentation output specifications. See :py:func:`render`.
    """


class HtmlOutputSpec(OutputSpec):
    """
    HTML documentation output.
    """

    def __init__(self, *, is_homepage: bool = False):
        """
        :param is_homepage: If to render output for a homepage with slight different stylings and behavior.
        """
        super().__init__()
        self.__is_homepage = is_homepage

    @property
    def is_homepage(self):
        return self.__is_homepage


class PdfOutputSpec(OutputSpec):
    """
    PDF documentation output.
    """


class PlaintextOutputSpec(OutputSpec):
    """
    Plaintext documentation output.
    """


class GeneratedDocument(annize.fs.FilesystemContent):

    def __init__(self, *, document: Document, output_spec: OutputSpec, culture: annize.i18n.Culture|None,
                 filename: str|None):
        super().__init__(self._path)
        self.__document = document
        self.__outputspec = output_spec
        self.__culture = culture
        self.__filename = filename

    def _path(self):
        if self.__culture:
            result = self.__document.generate(self.__outputspec, culture=self.__culture).file.path()
        else:
            result = self.__document.generate_all_cultures(self.__outputspec).file.path()
        if self.__filename:
            oresult = result
            result = annize.fs.fresh_temp_directory().path(self.__filename)
            oresult.move_to(result)
        return result
