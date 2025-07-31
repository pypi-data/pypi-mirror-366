# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Some preprocessor functions used by the materializer.

Only used internally by the parent package.
"""
import itertools
import typing as t

import annize.data
import annize.project


def resolve_appendtonodes(topnode: annize.project.Node) -> annize.project.Node:
    referencetuples = []
    def plan_references(node: annize.project.Node|None, childnodes: t.Iterable[annize.project.Node]) -> None:
        if isinstance(node, annize.project.ArgumentNode) and node.append_to:
            pkey = node.name = (node.name or annize.data.UniqueId().long_str)
            referencetuples.append((pkey, node.append_to))
        for childnode in childnodes:
            plan_references(childnode, childnode.children)
    plan_references(None, [topnode])
    unresolved_referencetuples = list(referencetuples)
    def create_references(node: annize.project.Node|None) -> None:
        if isinstance(node, annize.project.ArgumentNode):
            for referencetuple in referencetuples:
                originname, appendttoname = referencetuple
                if node.name == appendttoname:
                    keyrefnode = annize.project.ReferenceNode()
                    keyrefnode.reference_key = originname
                    keyrefnode.on_unresolvable = annize.project.ReferenceNode.OnUnresolvableAction.SKIP
                    node.append_child(keyrefnode)
                    if referencetuple in unresolved_referencetuples:
                        unresolved_referencetuples.remove(referencetuple)
        for childnode in node.children:
            create_references(childnode)
    create_references(topnode)
    if unresolved_referencetuples:
        raise annize.project.UnresolvableReferenceError(unresolved_referencetuples[0][1])
    return topnode


def normalize_blockscopes(topnode: annize.project.Node) -> annize.project.Node:
    def with_synthetic_blocks(fnodes: t.Iterable[annize.project.Node],
                              scope: annize.project.BlockNodeWithScope.Scope,
                              _nodes: t.Iterable[annize.project.Node] = None):
        if _nodes is None:
            return with_synthetic_blocks(fnodes, scope, fnodes)
        for node in _nodes:
            fnodes = with_synthetic_blocks(fnodes, scope, node.children)
            if isinstance(node, annize.project.BlockNodeWithScope) and node.scope == scope:
                if len(tuple(node.children)) > 0:
                    raise annize.project.MaterializerError(f"the node {node!r} must not have children")
                if (not node.parent) or (not isinstance(node.parent, annize.project.FileNode)):
                    raise annize.project.MaterializerError(f"the node {node!r} must be on top level of a file")
                blockclone = node.clone(with_children=False)
                node.parent.remove_child(node)
                blockclone.scope = annize.project.BlockNodeWithScope.Scope.BLOCK
                for fnode in fnodes:
                    blockclone.append_child(fnode)
                fnodes = [blockclone]
        return fnodes
    nnodes = []
    for fnode in topnode.children:
        topnode.remove_child(fnode)#TODO weirdo
        nnodes += with_synthetic_blocks([fnode], annize.project.BlockNodeWithScope.Scope.FILE)
    result = annize.project.BlockNode()
    for rnode in with_synthetic_blocks(nnodes, annize.project.BlockNodeWithScope.Scope.PROJECT):
        result.append_child(rnode)
    return result
