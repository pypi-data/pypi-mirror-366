# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage documentation section.
"""
import typing as t

import annize.flow.run_context
import annize.features.homepage.common
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, documentation: list[annize.features.documentation.common.Document],
                 head=annize.i18n.TrStr.tr("an_HP_Head_Documentation"), sort_index=30_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__documentation = documentation

    def pre_process_generate(self, info):
        info.custom_arg = {}
        for document in self.__documentation:
            documentdirname = annize.flow.run_context.object_name(document)
            output_spec = annize.features.documentation.common.HtmlOutputSpec()
            genres = document.generate_all_cultures(output_spec)
            genres.file.path().move_to(info.document_root_directory(documentdirname))
            info.custom_arg[document] = f"{info.document_root_url}{documentdirname}/index.html"

    def generate_content(self, info):
        if len(self.__documentation) > 0:
            product = annize.features.homepage.common.HomepageSection.Content()
            product.append_rst(annize.i18n.tr("an_HP_Doc_DocsAvailable"))
            for document in self.__documentation:
                generateddocumenturl = info.custom_arg[document]
                product.append_rst(f"`{document.title} <{generateddocumenturl}>`_")  # TODO document.title to base class, or use getattr here ?!
            return product
        return None
