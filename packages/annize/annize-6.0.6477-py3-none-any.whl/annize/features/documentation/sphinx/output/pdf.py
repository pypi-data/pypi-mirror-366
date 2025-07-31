# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based PDF documentation output.
"""
import os
import subprocess

import annize.features.documentation.sphinx.output.common
import annize.fs


@annize.features.documentation.sphinx.output.common.register_output_generator
class PdfOutputGenerator(annize.features.documentation.sphinx.output.common.OutputGenerator):
    """
    PDF documentation output.
    """

    @classmethod
    def is_compatible_for(cls, output_spec):
        return isinstance(output_spec, annize.features.documentation.common.PdfOutputSpec)

    def formatname(self):
        return "latex"

    def postproc(self, preresult: annize.fs.TInputPath) -> annize.fs.Path:
        preresult = annize.fs.Path(preresult)
        subprocess.check_call(["make"], cwd=preresult)
        for potresult in preresult.children():
            if potresult.name.endswith(".pdf"):
                return potresult
        raise RuntimeError("no pdf found in build output")
