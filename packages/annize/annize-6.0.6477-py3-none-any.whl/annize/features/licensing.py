# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project licensing information.
"""
import pathlib
import typing as t

import annize.asset
import annize.flow.run_context
import annize.i18n


class License:

    def __init__(self, *, name: annize.i18n.TrStr, text: annize.i18n.TrStr|None, **additional_info):
        self.__name = name
        self.__text = text
        self.__additional_info = dict(additional_info)

    @property
    def name(self) -> annize.i18n.TrStr:
        return self.__name

    @property
    def text(self) -> annize.i18n.TrStr|None:
        return self.__text

    def additional_info(self, key: str, *, default: t.Any = None) -> t.Any:
        return self.__additional_info.get(key, default)


def _license(name: str) -> t.Type[License]:
    class ALicense(License):
        def __init__(self):
            lictextpath = pathlib.Path(f"{annize.asset.data.licenses_dir}/{name}").read_text()
            super().__init__(name=annize.i18n.to_trstr(name), text=annize.i18n.to_trstr(lictextpath))
    return ALicense


AFLv3 = _license("AFL 3")
AGPLv3 = _license("AGPL 3")
Apache2 = _license("Apache 2")
Artistic1 = _license("Artistic 1")
BSD2clause = _license("BSD 2-clause")
BSD3clause = _license("BSD 3-clause")
Cc0v1 = _license("CC0 1.0")
CcBy3 = _license("CC BY 3.0")
CcByNc3 = _license("CC BY-NC 3.0")
CcByNcNd3 = _license("CC BY-NC-ND 3.0")
CcByNcSa3 = _license("CC BY-NC-SA 3.0")
CcByNd3 = _license("CC BY-ND 3.0")
CcBySa3 = _license("CC BY-SA 3.0")
GPLv3 = _license("GPL 3")
LGPLv3 = _license("LGPL 3")
MIT = _license("MIT")
MPLv11 = _license("MPL 1.1")
MPLv2 = _license("MPL 2")
PublicDomain = _license("Public Domain")


def project_licenses() -> list[License]:
    return annize.flow.run_context.objects_by_type(License)
