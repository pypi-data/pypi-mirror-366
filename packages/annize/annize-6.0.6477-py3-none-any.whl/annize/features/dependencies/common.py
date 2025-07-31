# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project dependency handling.
"""
import typing as t

import annize.i18n


class Kind:

    def __init__(self, *, label: annize.i18n.TrStr, importance: int):
        self.__label = label
        self.__importance = importance

    @property
    def label(self) -> annize.i18n.TrStr:
        return self.__label

    @property
    def importance(self) -> int:
        return self.__importance


class Dependency:

    def __init__(self, *, kind: Kind|None, label: annize.i18n.TrStr|None,
                 comment: annize.i18n.TrStr|None, icon: str|None, importance: int = 0):
        self.__kind = kind or Required()
        self.__label = label
        self.__comment = comment
        self.__icon = icon
        self.__importance = importance

    @property
    def kind(self) -> Kind:
        return self.__kind

    @property
    def label(self) -> annize.i18n.TrStr:
        return self.__label

    @property
    def comment(self) -> annize.i18n.TrStr:
        return self.__comment

    @property
    def icon(self) -> str:
        return self.__icon

    @property
    def importance(self) -> int:
        return self.__importance


class Required(Kind):

    def __init__(self, **b):
        super().__init__(label=annize.i18n.TrStr.tr("an_Dep_Required"), importance=0, **b)


class Recommended(Kind):

    def __init__(self, **b):
        super().__init__(label=annize.i18n.TrStr.tr("an_Dep_Recommended"), importance=-200_000, **b)


class Included(Kind):

    def __init__(self, **b):
        super().__init__(label=annize.i18n.TrStr.tr("an_Dep_Included"), importance=-400_000, **b)


class GnuLinux(Dependency):

    def __init__(self, *, kind=None, comment):
        super().__init__(kind=kind or Recommended(), label=annize.i18n.TrStr.tr("an_Dep_GnuLinux"), icon="linux", comment=comment)


class Artwork(Dependency):  # pylint: disable=redefined-builtin

    def __init__(self, *, kind=None, label, origin: str, comment, license: str|None):#TODO zz license:License
        class FullComment(annize.i18n.TrStr):
            def get_variant(self, culture):
                full_comment = []
                if comment:
                    full_comment.append(str(comment))
                if license:
                    full_comment.append(annize.i18n.tr("an_Dep_Artwork_License").format(**locals()))
                if origin:
                    full_comment.append(f"`{annize.i18n.tr('an_Dep_Artwork_Origin')} <{origin}>`__")
                return "; ".join(full_comment)
        super().__init__(kind=kind or Included(), label=label, icon="artwork", comment=FullComment())


def dependencies_to_rst_text(dependencies: list[Dependency]) -> str:
    content = ""
    dependencies = sorted(dependencies, key=lambda dep: (-dep.kind.importance, -dep.importance, type(dep).__name__,
                                                         dep.icon or "~", str(dep.label)))
    for dependency in dependencies:
        if not dependency.label:
            continue
        icon = dependency.icon or "misc"
        comment = f" ({dependency.comment})" if dependency.comment else ""
        label = str(dependency.label).replace("`", "'")
        kind = dependency.kind.label
        dlm = ": " if (len(comment) > 0) else ""
        content += f"\n|annizeicon_{icon}| {kind}: **{label}**{comment}\n\n"
    return content
