# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BlockBehavior`.
"""
import contextlib

import annize.project.materializer.behaviors


class BlockBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles block.
    """

    @contextlib.contextmanager
    def node_context(self, nodemat):
        yield
        if isinstance(nodemat.node, (annize.project.BlockNode, annize.project.FileNode)):
            nodemat.set_materialized_result(nodemat.get_materialized_children())
