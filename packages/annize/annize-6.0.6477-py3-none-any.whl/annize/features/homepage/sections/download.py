# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage download section.
"""
import hashlib
import locale
import typing as t

import annize.features.base
import annize.features.dependencies.common
import annize.features.distributables.common
import annize.features.documentation.sphinx.rst
import annize.features.homepage.common
import annize.fs
import annize.i18n


class Section(annize.features.homepage.common.HomepageSection):

    def __init__(self, *, distributables: list[annize.features.distributables.common.Group],
                 dependencies: list[annize.features.dependencies.common.Dependency],
                 head=annize.i18n.TrStr.tr("an_HP_Head_Download"), sort_index=40_000):
        super().__init__(head=head, sort_index=sort_index)
        self.__distributables = distributables
        self.__dependencies = dependencies

    def __generate_packagelist(self, info: annize.features.homepage.common.HomepageSection._GenerateInfo):
        content = ""
        lblfile = annize.i18n.tr("an_HP_DL_File")
        lblreleasetime = annize.i18n.tr("an_HP_DL_Releasedate")
        lblsha256sum = annize.i18n.tr("an_HP_DL_Sha256sum")
        lblsize = annize.i18n.tr("an_HP_DL_Size")
        info.custom_arg = []  # TODO now we do that once per language (as its called in generate_content())
        for dlgroup in self.__distributables:
            groupcontent = f".. rubric:: {dlgroup.title}\n\n{dlgroup.description}\n\n"
            for dlfile in dlgroup.files():
                fdlfile = dlfile.path()
                info.custom_arg.append(fdlfile)
                ctime = fdlfile.ctime().strftime("%x")
                fhash = filehash(fdlfile)
                ssize = friendly_filesize(fdlfile.file_size())
                groupcontent += (f".. rst-class:: downloadblock\n\n"
                                 f":{lblfile}: `{fdlfile.name} <{info.document_root_url}{fdlfile.name}>`_\n"
                                 f":{lblreleasetime}: {ctime}\n"
                                 f":{lblsha256sum}: :samp:`{fhash}`\n"
                                 f":{lblsize}: {ssize}\n\n")
            content += groupcontent
        return content

    def pre_process_generate(self, info):
        for dlgroup in self.__distributables:
            for dlfile in dlgroup.files():
                dlfile.path()

    def post_process_generate(self, info):
        dlfiles: list[annize.fs.Path] = info.custom_arg
        for dlfile in dlfiles:
            dlfile.copy_to(info.document_root_directory(dlfile.name))

    def generate_content(self, info):  # TODO make package generation in "en" culture context ?!
        project_name = annize.features.base.pretty_project_name()
        product = annize.features.homepage.common.HomepageSection.Content()
        depslist = annize.features.dependencies.common.dependencies_to_rst_text(self.__dependencies)
        packagelist = self.__generate_packagelist(info)
        do_return = False
        if packagelist:
            do_return = True
            pkghead = annize.i18n.tr("an_HP_DL_PackagesAvailable")
            if depslist:
                thereqs = annize.i18n.tr("an_HP_DL_TheReqs")
                dependenciesref = f":ref:`{thereqs}<hp_downl_deps>`"
                pkghead += " " + annize.i18n.tr("an_HP_DL_CheckReqs").format(**locals())
            product.append_rst(pkghead)
            product.append_rst(packagelist)
        if depslist:
            do_return = True
            product.append_rst(annize.features.documentation.sphinx.rst.RstGenerator.heading(
                annize.i18n.tr("an_HP_DL_Deps"), sub=True, anchor="hp_downl_deps"))
            product.append_rst(annize.i18n.tr("an_HP_DL_Uses3rdParty").format(**locals()))
            product.append_rst(depslist)
        return product if do_return else None


def friendly_filesize(isize: int) -> str:
    ssize = annize.i18n.tr("an_HP_DL_FriendlySize_B")
    for nssize in [
        annize.i18n.tr("an_HP_DL_FriendlySize_kB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_MB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_GB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_TB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_PB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_EB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_ZB"),
        annize.i18n.tr("an_HP_DL_FriendlySize_YB")
    ]:
        if isize > 1024:
            isize = isize / 1024.0
            ssize = nssize
        else:
            break
    sisize = locale.format_string("%.1f", isize)
    return f"{sisize} {ssize}"


def filehash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            block = f.read(1024 ** 2)
            if block == b"":
                break
            hasher.update(block or b"")
    return hasher.hexdigest()


# TODO noh packagestore (show last three versions via packagestore)
