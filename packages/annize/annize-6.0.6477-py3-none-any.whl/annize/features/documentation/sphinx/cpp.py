# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based C/C++ documentation.
"""
import annize.features.documentation.sphinx.doxygen_compat


class CppApiReferenceLanguage(annize.features.documentation.sphinx.doxygen_compat.DoxygenSupportedApiReferenceLanguage):
    """
    C++ language support for api references.
    """

    def __init__(self, **kwargs):
        super().__init__(file_patterns="*.c *.cc *.cxx *.cpp *.c++ *.ii *.ixx *.ipp *.i++ *.inl *.idl *.ddl *.h *.hh"
                                       " *.hxx *.hpp *.h++", **kwargs)
