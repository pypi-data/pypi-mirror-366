# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage media gallery section.
"""
import typing as t

import annize.flow.run_context
import annize.features.documentation.sphinx.rst
import annize.features.homepage.common
import annize.features.media_galleries
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, head=annize.i18n.TrStr.tr("an_HP_Head_Gallery"), sort_index=50_000,
                 media_galleries: list[annize.features.media_galleries.Gallery]):
        super().__init__(head=head, sort_index=sort_index)
        self.__mediagalleries = media_galleries

    def pre_process_generate(self, info):
        info.custom_arg = {}
        for gallery in self.__mediagalleries:
            gallerydirname = annize.flow.run_context.object_name(gallery)
            gallerydir = info.document_root_directory(gallerydirname)
            gallerydir.mkdir()
            info.custom_arg[gallery] = galleryitems = []
            for item in gallery.items:
                fitem = item.file.path()
                itemfile = gallerydir(fitem.name)
                fitem.copy_to(itemfile)
                galleryitems.append((item, f"{info.document_root_url}{gallerydirname}/{itemfile.name}"))

    def generate_content(self, info):
        if len(self.__mediagalleries) > 0:
            product = annize.features.homepage.common.HomepageSection.Content()
            for mediagallery in self.__mediagalleries:
                if mediagallery.title:
                    product.append_rst(annize.features.documentation.sphinx.rst.RstGenerator.heading(mediagallery.title,
                                                                                                    variant="~"))
                galleryrst = ".. rst-class:: annizedoc-mediagallery\n\n"
                for item, itemurl in info.custom_arg[mediagallery]:
                    mtitle = str(item.description or "").replace("\n", " ").replace('"', "''")
                    galleryrst += f" `{mtitle} <{itemurl}#{item.mediatype.value}>`__\n"
                product.append_rst(galleryrst)
            return product
        return None
