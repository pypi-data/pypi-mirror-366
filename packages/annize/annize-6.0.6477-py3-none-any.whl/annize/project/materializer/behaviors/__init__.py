# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Behaviors.

See :py:class:`Behavior`.
"""
import abc
import typing as t

import annize.project.materializer.core


class Behavior(abc.ABC):
    """
    A behavior implements what the materializer does for a given node. See subclasses in the submodules.
    """

    @abc.abstractmethod
    def node_context(self, nodemat: "annize.project.materializer.core.NodeMaterialization") -> t.ContextManager:
        """
        For a node, the materializer will enter the context returned by this function for all behaviors.

        The materializer itself does that for the root node. Behaviors itself are responsible for triggering that
        same process on children.

        So, any node gets materialized in the context of all behaviors on all parent nodes. Actual materialization logic
        happens in this function, in the course of setting up and taking down all these contexts.

        :param nodemat: The node materialization for the current node.
        """
