# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage license section.
"""
import annize.features.base
import annize.features.homepage.common
import annize.features.licensing
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, head=annize.i18n.TrStr.tr("an_HP_Head_License"), sort_index=20_000):
        super().__init__(head=head, sort_index=sort_index)

    def generate_content(self, info):
        licenses = annize.features.licensing.project_licenses()
        if len(licenses) > 0:
            project_name = annize.features.base.pretty_project_name() or annize.i18n.tr("an_ThisProject")
            licdescs = []
            for ilic, lic in enumerate(licenses):
                if lic.text:
                    licfilename = f"_license_{ilic}.txt"
                    info.document_variant_directory(licfilename).write_file(str(lic.text))
                    licdescs.append(f"`{lic.name} <{info.document_variant_url}{licfilename}>`_")
                else:
                    licdescs.append(str(lic.name))
            license_names = annize.i18n.friendly_join_string_list([str(lic.name) for lic in licenses])
            return annize.features.homepage.common.HomepageSection.Content(rst_text=annize.i18n.tr("an_HP_Lic_Text").format(**locals()))
        return None
