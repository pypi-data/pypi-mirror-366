# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage changelog section.
"""
import datetime
import typing as t

import annize.features.changelog.common
import annize.features.documentation.sphinx.rst
import annize.features.homepage.common
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, changelog: annize.features.changelog.common.Changelog|None,
                 head=annize.i18n.TrStr.tr("an_HP_Head_Changelog"), sort_index=60_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__changelog = changelog

    def generate_content(self, info):
        changelog = self.__changelog or annize.features.changelog.common.default_changelog()
        if changelog:
            entries = changelog.entries
            entries.sort(key=lambda e: (e.time, e.version))
            entries.reverse()
            if len(entries) > 0:
                product = annize.features.homepage.common.HomepageSection.Content()
                now = datetime.datetime.now()
                for ientry, entry in enumerate(entries):
                    if (ientry > 0) and entry.time and (now - entry.time > datetime.timedelta(days=365)):
                        break
                    product.append_rst("")  # TODO
                    entryhead = []
                    if entry.time:
                        entryhead.append(entry.time.date().strftime("%x"))
                    if entry.version:
                        entryhead.append(str(entry.version))
                    if len(entryhead) == 0:
                        raise ValueError("Changelog entries must have a `time` or a `version`")
                    product.append_rst(annize.features.documentation.sphinx.rst.RstGenerator.heading(
                        ", ".join(entryhead), sub=True))
                    for entryitem in entry.items:
                        product.append_rst("- " + str(entryitem.text).strip().replace("\n", "  \n"))
                return product
        return None
