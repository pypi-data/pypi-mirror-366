# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Media galleries.
"""
import enum
import mimetypes
import typing as t

import annize.fs
import annize.i18n


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Gallery:

    class Item:

        def __init__(self, file: annize.fs.FilesystemContent, description: annize.i18n.TrStr|None, mediatype: MediaType):
            self.__file = file
            self.__description = description
            self.__mediatype = mediatype

        @property
        def file(self) -> annize.fs.FilesystemContent:
            return self.__file

        @property
        def description(self) -> annize.i18n.TrStr|None:
            return self.__description

        @property
        def mediatype(self) -> MediaType:
            return self.__mediatype

    def __init__(self, *, source: annize.fs.FilesystemContent, title: annize.i18n.TrStr|None):
        self.__source = source
        self.__title = title or annize.i18n.to_trstr("")

    @property
    def items(self) -> list[Item]:
        result = []
        for itemfile in self.__source.path().children():
            itemmime = mimetypes.guess_type(itemfile.name)[0] or "/"
            mediatype = {"image": MediaType.IMAGE,
                         "video": MediaType.VIDEO}.get(itemmime.split("/")[0])
            if mediatype:
                result.append(self.Item(itemfile, self._description_for_mediafile(itemfile), mediatype))
        return result

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    def _description_for_mediafile(self, itemfile: annize.fs.FilesystemContent) -> annize.i18n.TrStr:
        variants = {}
        itemfile = annize.fs.Path(itemfile)
        txtfiles = [tfl for tfl in itemfile.parent.children() if tfl.name.endswith(".txt")]
        for varfile in [tfl for tfl in txtfiles if tfl.name.startswith(f"{itemfile.name}.")]:
            varname = varfile.name[len(itemfile.name)+1:-4]
            variants[varname] = varfile.read_bytes().decode().strip()
        otxtfile = itemfile.parent(f"{itemfile.name}.txt")
        if otxtfile.exists():
            variants["?"] = otxtfile.read_bytes().decode()  # TODO
        class ATrStr(annize.i18n.TrStr):
            def get_variant(self, culture):
                return variants.get(culture.iso_639_1_language_code, None)
        return ATrStr()
