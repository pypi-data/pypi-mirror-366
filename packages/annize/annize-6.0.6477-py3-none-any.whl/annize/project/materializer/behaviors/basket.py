# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BasketBehavior`.
"""
import contextlib

import annize.project.materializer.behaviors


class BasketBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles baskets.
    """

    @contextlib.contextmanager
    def node_context(self, nodemat):
        yield
        if nodemat.has_result:
            newresult = []
            for resultitem in nodemat.result:
                if getattr(resultitem, "_is_annize_basket", False) \
                        or isinstance(resultitem, annize.data.Basket):
                    newresult += resultitem
                else:
                    newresult.append(resultitem)
            nodemat.set_materialized_result(newresult)
