# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based plaintext documentation output.
"""
import annize.features.documentation.sphinx.output.common


@annize.features.documentation.sphinx.output.common.register_output_generator
class PlaintextOutputGenerator(annize.features.documentation.sphinx.output.common.OutputGenerator):
    """
    Plaintext documentation output.
    """

    @classmethod
    def is_compatible_for(cls, output_spec):
        return isinstance(output_spec, annize.features.documentation.common.PlaintextOutputSpec)

    def formatname(self):
        return "text"
