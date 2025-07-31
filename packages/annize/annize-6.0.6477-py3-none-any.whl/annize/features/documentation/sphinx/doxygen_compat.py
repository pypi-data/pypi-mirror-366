# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based documentation with Doxygen support.
"""
import os
import subprocess
import typing as t

import annize.features.documentation.sphinx.common

# pylint: disable=unused-variable,arguments-differ,undefined-variable ## TODO weg


class DoxygenSupportedApiReferenceLanguage(annize.features.documentation.sphinx.common.ApiReferenceLanguage):
    """
    Language support for api references powered by Doxygen.
    """

    def __init__(self, *, _doxygenopts: dict[str, str]|None = None, extract_all: bool = True,
                 extract_private: bool = True, extract_package: bool = True, extract_static: bool = True,
                 extract_local_classes: bool = True, extract_local_methods: bool = True,
                 extract_anon_nspaces: bool = True, extract_priv_virtual: bool = True, file_patterns: str = "*",
                 inline_inherited_memb: bool = True, inherit_docs: bool = True,
                 hide_undoc_members: bool = False, hide_undoc_classes: bool = False,
                 exclude_patterns: str = "", predefined: list[str]|None = None):
        def _b(val: bool) -> str:
            return "YES" if val else "NO"
        self.__doxygenopts = {
            "GENERATE_XML": "YES", "XML_OUTPUT": "_doxygen_xml", "EXTRACT_ALL": _b(extract_all),
            "EXTRACT_PRIVATE": _b(extract_private), "EXTRACT_PACKAGE": _b(extract_package),
            "EXTRACT_STATIC": _b(extract_static), "EXTRACT_LOCAL_CLASSES": _b(extract_local_classes),
            "EXTRACT_LOCAL_METHODS": _b(extract_local_methods), "EXTRACT_ANON_NSPACES": _b(extract_anon_nspaces),
            "EXTRACT_PRIV_VIRTUAL": _b(extract_priv_virtual), "HIDE_UNDOC_MEMBERS": _b(hide_undoc_members),
            "HIDE_UNDOC_CLASSES": _b(hide_undoc_classes), "GENERATE_HTML": "NO", "GENERATE_LATEX": "NO",
            "INLINE_INHERITED_MEMB": _b(inline_inherited_memb), "INHERIT_DOCS": _b(inherit_docs),
            "RECURSIVE": "YES", "FILE_PATTERNS": file_patterns, "EXCLUDE_PATTERNS": exclude_patterns,
            "PREDEFINED": " ".join(predefined or []), **(_doxygenopts or {})}

    def __info(self, outpath):
        project = os.path.basename(outpath)
        parpath = os.path.abspath(f"{outpath}/..")
        tmpoutpath = f"{parpath}/_tmp/{os.path.basename(outpath)}"
        doxygenxmlpath = f"{tmpoutpath}/_doxygen_xml"
        return project, tmpoutpath, doxygenxmlpath

    def __prepare_generate(self, rootpath, outpath):
        annize.utils.basic.verify_tool_installed("doxygen")
        annize.utils.basic.verify_tool_installed("breathe-apidoc")
        project, tmpoutpath, doxygenxmlpath = self.__info(outpath)
        return (f"extensions.append('breathe')\n"
                f"breathe_default_members = ('members', 'private-members', 'undoc-members')\n"
                f"breathe_projects = {{ {repr(project)}: {repr(doxygenxmlpath)} }}\n")

    def generate_sources(self, srcpath, intstructpath, confdirpath, heading):
        self.__prepare_generate(foo)
        project, tmpoutpath, doxygenxmlpath = self.__info(outpath)
        super().generate_sources(srcpath, tmpoutpath, confdirpath, heading)
        with open(f"{tmpoutpath}/_doxygen_conf", "w") as f:
            for key, val in {**self.__doxygenopts, "STRIP_FROM_PATH": tmpoutpath}.items():
                f.write(f"{key} = {val}\n")
            f.write("EXTENSION_MAPPING += js=JavaScript")
        subprocess.check_call(["doxygen", "_doxygen_conf"], cwd=tmpoutpath)
        subprocess.check_call(["breathe-apidoc", "-o", outpath, "-p", os.path.basename(outpath),
                               "-g", "class,interface,struct,union,namespace,group", doxygenxmlpath])
        with open(f"{outpath}.rst", "w") as f:
            f.write(f"""{docgen.heading(heading)}
.. toctree::
   :glob:

   {os.path.basename(outpath)}/*
""")
