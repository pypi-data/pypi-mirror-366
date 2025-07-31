# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Inner core parts of the project materializer. Only used internally by the parent package.
"""
import contextlib
import itertools
import logging
import typing as t

import annize.flow.run_context
import annize.project

if t.TYPE_CHECKING:
    import annize.project.feature_loader
    import annize.project.materializer.behaviors


_logger = logging.getLogger(__name__)

_Material = t.Any

_Materialization = t.Tuple[annize.project.Node, list[_Material]]


class NodeMaterialization:

    def __init__(self, materializer: "ProjectMaterializer", node: annize.project.Node, store: dict):
        self.__node = node
        self.__materializer = materializer
        self.__store = store
        self.__result = None
        self.__problems = []

    @property
    def node(self) -> annize.project.Node:
        return self.__node

    def set_materialized_result(self, resultlist):
        self.__result = resultlist

    def set_problems(self, problems: t.Iterable[Exception]):
        self.__problems = list(problems)

    def get_materialized_children_tuples(self):
        return self.__materializer._materialize_hlp_childobjs(self.__node, self.__store)

    def get_materialized_children(self) -> t.Iterable[_Material]:
        return list(itertools.chain.from_iterable([x[1] for x in self.get_materialized_children_tuples()]))

    def try_get_materialization_for_node(self, node: annize.project.Node):
        return self.__store.get(node, None)

    @property
    def has_result(self):
        return self.__result is not None

    @property
    def result(self):
        if not self.has_result:
            raise RuntimeError("no result available")
        return self.__result

    @property
    def problems(self) -> list[Exception]:
        return self.__problems


class ProjectMaterializer:

    def __init__(self, node: annize.project.Node, *,
                 behaviors: t.Iterable["annize.project.materializer.behaviors.Behavior"]):
        self.__node = node
        self.__behaviors = behaviors

    def __materialization_for_node(self, node: annize.project.Node, store: dict) -> NodeMaterialization:
        result = store.get(node, None)
        if not result:
            result = store[node] = NodeMaterialization(self, node, store)
        return result

    def __materialize(self, node: annize.project.Node, store: dict) -> None:
        nodemat = self.__materialization_for_node(node, store)
        _logger.debug("Starting materialization of '%s'; nodemat.has_result=%r", node, nodemat.has_result)
        if not nodemat.has_result:
            nodemat.set_problems([])
            try:
                with contextlib.ExitStack() as stack:
                    for behavior in self.__behaviors:
                        stack.enter_context(behavior.node_context(nodemat))
            except Exception as ex:
                nodemat.set_problems([ex])
        #TODO _logger.debug("Finalized materialization of '%s' to '%s'", node, nodemat.result)

    def _materialize_hlp_childobjs(self, node: annize.project.Node, store: dict) -> list[_Materialization]:
        _logger.debug("Starting materialization of the children of '%s'", node)
        result = []
        children_have_errors = False
        for icnode, cnode in enumerate(node.children):
            self.__materialize(cnode, store)
            cnodemat = self.__materialization_for_node(cnode, store)
            if cnodemat.has_result:
                result.append((cnode, cnodemat.result))
            else:
                children_have_errors = True
        _logger.debug("Finished materialization of the children of '%s' to %d items", node, len(result))
        if children_have_errors:
            raise ChildrenNotMaterializableError(node)
        return result

    def __get_erroneous_nodes(self, materializationstore, old_erroneous_nodes):  # TODO rename
        new_erroneous_nodes = set()
        for node, nodemat in materializationstore.items():
            if nodemat.problems:
                new_erroneous_nodes.add(node)
        if new_erroneous_nodes:
            if old_erroneous_nodes is None:
                retry = True
            else:
                retry = len(old_erroneous_nodes - new_erroneous_nodes) > 0
        else:
            retry = False
        return new_erroneous_nodes, retry

    def get_materialized(self) -> t.Tuple[list[t.Any]|None, dict[annize.project.Node, list[Exception]]]:
        materializationstore = {}
        erroneous_nodes = None
        retry = True
        nodemat = self.__materialization_for_node(self.__node, materializationstore)
        while retry:
            _logger.debug("Beginning project materialization attempt.")
            self.__materialize(self.__node, materializationstore)
            erroneous_nodes, retry = self.__get_erroneous_nodes(materializationstore, erroneous_nodes)
        print("TODO fr", nodemat.has_result)
        if nodemat.has_result:
            for obj in nodemat.result:
                annize.flow.run_context.current().mark_object_as_toplevel(obj)
            result = nodemat.result
        else:
            result = None
        errors = {node: materializationstore[node].problems for node in erroneous_nodes}
        return result, errors


class InternalError(Exception):
    pass


class ChildrenNotMaterializableError(InternalError):

    def __init__(self, node: annize.project.Node):
        super().__init__(f"Children of '{node}' not materializable")
