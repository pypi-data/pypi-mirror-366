# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project versioning.
"""
import typing as t

import annize.flow.run_context
import annize.data


class Line:

    def __init__(self, *, version: annize.data.Version):
        self.__version = version

    @property
    def version(self) -> annize.data.Version:
        return self.__version


class Version(annize.data.Version):

    def __init__(self, *, text: str|None, pattern: annize.data.version.VersionPattern|None,
                 **segment_values):
        super().__init__(text=text, pattern=pattern or default_version_pattern(), **segment_values)


_CONTEXT__DEFAULT_VERSION_PATTERN = annize.data.UniqueId("default_version_pattern").processonly_long_str


def default_version_pattern() -> annize.data.version.VersionPattern:
    return annize.flow.run_context.object_by_name(_CONTEXT__DEFAULT_VERSION_PATTERN) or CommonVersionPattern()


def project_versions() -> list[annize.data.Version]:
    return annize.flow.run_context.objects_by_type(annize.data.Version)


#TODO class VersionPattern


class CommonVersionPattern(annize.data.version.VersionPattern):

    def __init__(self):
        super().__init__(segments=[
            annize.data.version.NumericVersionPatternSegment(partname="major"),
            annize.data.version.SeparatorVersionPatternSegment(text="."),
            annize.data.version.NumericVersionPatternSegment(partname="minor"),
            annize.data.version.OptionalVersionPatternSegment(segments=[
                annize.data.version.SeparatorVersionPatternSegment(text="."),
                annize.data.version.NumericVersionPatternSegment(partname="build")
            ])
        ])
