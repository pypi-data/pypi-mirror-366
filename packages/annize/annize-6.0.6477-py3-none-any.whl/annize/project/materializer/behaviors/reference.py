# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ReferenceBehavior`.
"""
import contextlib

import annize.flow.run_context
import annize.project.materializer.behaviors


class ReferenceBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles reference nodes.
    """

    def __init__(self):
        super().__init__()

    @contextlib.contextmanager
    def node_context(self, nodemat):
        yield
        if isinstance(nodemat.node, annize.project.ReferenceNode):
            obj = annize.flow.run_context.object_by_name(nodemat.node.reference_key, self)
            if obj == self:
                raise annize.project.UnresolvableReferenceError(nodemat.node.reference_key)
            nodemat.set_materialized_result([obj])
