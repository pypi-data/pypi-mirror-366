# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage imprint section.
"""
import annize.features.base
import annize.features.homepage.common
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, imprint: annize.i18n.TrStr, head=annize.i18n.TrStr.tr("an_HP_Head_Imprint"),
                 sort_index=70_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__imprint = imprint

    def generate_content(self, info):
        imprint = annize.features.base.imprint() if (self.__imprint is None) else self.__imprint
        return annize.features.homepage.common.HomepageSection.Content(rst_text=annize.i18n.tr_if_trstr(imprint)) if imprint else None
