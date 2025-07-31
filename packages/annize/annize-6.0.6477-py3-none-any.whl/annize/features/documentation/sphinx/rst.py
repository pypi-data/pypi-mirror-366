# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based reStructuredText documentation.
"""
import annize.i18n


#TODO

class RstGenerator:
    """
    Generator for some documentation source parts.
    """

    @staticmethod
    def heading(text: annize.i18n.TrStrOrStr, *, variant: str = "=", sub: bool = False,
                anchor: str|None = None) -> str:
        #TODO refactor that mess (large module name; unclear usage of variant/sub)
        """
        Generates documentation source for a section heading.
        """
        text = str(text)
        hrule = (variant * len(text))
        return "\n\n" + (f".. _{anchor}:\n\n" if anchor else "") + ("" if sub else f"{hrule}\n") \
               + f"{text}\n{hrule}\n\n"
