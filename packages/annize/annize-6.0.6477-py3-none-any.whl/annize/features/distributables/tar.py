# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tarballs.
"""
import subprocess
import typing as t

import annize.object
import annize.data
import annize.features.licensing
import annize.fs
import annize.i18n


if False:
    annize.i18n.tr("an_int_SourceTarPackage")  # to be used by Annize projects


class Package(annize.fs.FilesystemContent):

    def _path(self):
        name = self.__packagename or annize.features.base.project_name()
        sauxversion = f"-{self.__version}" if self.__version else ""
        sauxnamepostfix = f"-{self.__packagenamepostfix}" if self.__packagenamepostfix else ""
        pkgroot = f"{name}{sauxversion}{sauxnamepostfix}"
        tarsrc = self.__source.path().temp_clone(basename=pkgroot)
        #TODO with self.__source.path().temp_clone(basename=pkgroot) as tarsrc:
        if self.__documentation:
            self.__documentation.path().copy_to(tarsrc, destination_as_parent=True)
        license = self.__license or annize.features.licensing.project_licenses()[0]  # TODO
        tarsrc("LICENSE").write_file(license.text)
        resultdir = annize.fs.fresh_temp_directory().path
        result = resultdir(f"{pkgroot}.tgz")
        # TODO use "tarfile" module instead
        subprocess.check_call(["tar", "cfz", result, pkgroot], cwd=tarsrc.parent)
        return result

    @annize.object.explicit_only("documentation")
    def __init__(self, *, packagename: str|None, packagenamepostfix: str|None,
                 source: annize.fs.FilesystemContent, version: annize.data.Version|None,
                 license: annize.features.licensing.License|None,
                 documentation: annize.fs.FilesystemContent|None):
        super().__init__(self._path)
        self.__packagename = packagename
        self.__packagenamepostfix = packagenamepostfix
        self.__source = source
        self.__version = version
        self.__license = license
        self.__documentation = documentation
