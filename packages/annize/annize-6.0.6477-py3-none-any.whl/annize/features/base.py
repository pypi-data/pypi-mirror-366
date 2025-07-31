# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project base information.
"""
import datetime
import os
import typing as t

import annize.flow.run_context
import annize.data
import annize.fs
import annize.features.files
import annize.i18n
import annize.project.loader


class Data:

    def __init__(self, *, project_name: str = None,
                 pretty_project_name: annize.i18n.TrStr|None = None,
                 summary: annize.i18n.TrStr|None = None,
                 long_description: annize.i18n.TrStr|None = None,
                 homepage_url: str|None = None,
                 imprint: annize.i18n.TrStr|None = None,
                 project_directory: str|None = None):
        self.__project_name = project_name  # TODO whitelist allowed characters
        self.__pretty_project_name = pretty_project_name
        self.__summary = summary
        self.__long_description = long_description
        self.__homepage_url = homepage_url
        self.__imprint = imprint
        self.__project_directory = project_directory

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def pretty_project_name(self) -> annize.i18n.TrStr:
        return self.__pretty_project_name

    @property
    def summary(self) -> annize.i18n.TrStr:
        return self.__summary

    @property
    def long_description(self) -> annize.i18n.TrStr:
        return self.__long_description

    @property
    def homepage_url(self) -> str:
        return self.__homepage_url

    @property
    def imprint(self) -> annize.i18n.TrStr:
        return self.__imprint

    @property
    def project_directory(self) -> str:
        return self.__project_directory


class BrandColor(annize.data.Color):
    pass


class DateTime(datetime.datetime):

    def __new__(cls, *, iso: str):
        return datetime.datetime.fromisoformat(iso)


class Keywords:

    def __init__(self, *, from_string: str = "", split_by: str = " ", keywords: list[str] = ()):
        self.__from_string = from_string
        self.__split_by = split_by
        self.__keywords = keywords

    @property
    def keywords(self) -> list[str]:
        result = []
        for keyword in [*self.__keywords, *self.__from_string.split(self.__split_by)]:
            if keyword and (keyword not in result):
                result.append(keyword)
        return result


class Keyword(Keywords):

    def __init__(self, text: str):
        super().__init__(keywords=[text])


def project_keywords() -> Keywords:
    allkeywords = []
    for keywords in annize.flow.run_context.objects_by_type(Keywords):
        for keyword in keywords.keywords:
            if keyword not in allkeywords:
                allkeywords.append(keyword)
    return Keywords(keywords=allkeywords)


class Basket(annize.data.Basket):  # TODO have it directly in annize namespace?!

    def __init__(self, *, items: list[object]):
        super().__init__(items)


class FirstOf(annize.data.Basket):

    def __init__(self, *, objects: list[object]):
        super().__init__(objects[:1])


def brand_color(*, none_on_undefined: bool = False) -> annize.data.Color:
    for obj in annize.flow.run_context.objects_by_type(BrandColor):
        return obj
    return None if none_on_undefined else annize.data.Color(red=0.3, green=0.3, blue=0.3)


def _get_data(key: str, default: t.Any) -> t.Any:
    result = default
    for obj in annize.flow.run_context.objects_by_type(Data):
        value = getattr(obj, key)
        if value:
            result = value
            break
    return result


def project_name() -> str:
    return _get_data("project_name", "")


def pretty_project_name() -> annize.i18n.TrStr:
    return _get_data("pretty_project_name", project_name())


def summary() -> annize.i18n.TrStr:
    return _get_data("summary", "")


def long_description() -> annize.i18n.TrStr:
    return _get_data("long_description", "")


def homepage_url() -> str:
    return _get_data("homepage_url", "")


def imprint() -> annize.i18n.TrStr:
    return _get_data("imprint", "")


def project_directory() -> annize.fs.Path:
    annize_config_rootpath = annize.fs.Path(annize.flow.run_context.object_by_name(
        annize.flow.run_context.RunContext.ANNIZE_CONFIG_ROOTPATH__NAME))

    result = _get_data("project_directory", None)
    if not result:
        result = annize.project.loader.project_root_directory(annize_config_rootpath)
    result = annize.fs.Path(result)
    if not result.is_absolute():
        result = annize_config_rootpath.parent(result)
    return result
