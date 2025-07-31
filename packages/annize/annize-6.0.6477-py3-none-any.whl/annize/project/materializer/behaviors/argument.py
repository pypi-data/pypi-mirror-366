# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ArgumentBehavior` and :py:class:`AssociateArgumentNodeBehavior`.
"""
import contextlib
import inspect
import typing as t

import annize.flow.run_context
import annize.data
import annize.project.materializer.behaviors
import annize.project.feature_loader


class ArgumentBehavior(annize.project.materializer.behaviors.Behavior):
    """
    Behavior that handles argument nodes (incl. creation of an object for an object node).
    """

    def __init__(self, callfct, *, feature_loader: annize.project.feature_loader.FeatureLoader):
        # TODO xx remove those params from Materializer itself TODO type_hints
        self.__featureloader = feature_loader
        self.__callfct = callfct

    @contextlib.contextmanager
    def node_context(self, nodemat):
        yield
        if isinstance(nodemat.node, annize.project.ObjectNode):
            args, kwargs = list(), dict()
            for childnode, childarguments in nodemat.get_materialized_children_tuples():
                if len(childarguments) > 0:
                    if isinstance(childnode, annize.project.ArgumentNode) and childnode.arg_name:
                        kwargs[childnode.arg_name] = childarguments[0]
                    else:
                        args += childarguments
            featuremodule = self.__featureloader.load_feature(nodemat.node.feature)
            if not featuremodule:
                raise annize.project.FeatureUnavailableError(nodemat.node.feature)
            try:
                clss = getattr(featuremodule, nodemat.node.type_name)
            except AttributeError as ex:
                raise annize.project.MaterializerError(
                    f"no item {nodemat.node.type_name!r} in feature module {nodemat.node.feature!r}") from ex
            clssspec = inspect.getfullargspec(clss)
            if len(clssspec.args) > 1 or clssspec.varargs:
                raise annize.project.MaterializerError(f"callable {nodemat.node.type_name!r} in {nodemat.node.feature!r}"
                                                       f" has position arguments, which is not allowed")
            try:
                value = self.__callfct(clss, args, kwargs)
            except TypeError as ex:
                raise annize.project.MaterializerError(f"unable to construct"
                                                       f" '{nodemat.node.feature}.{nodemat.node.type_name}', {ex}") from ex
        elif isinstance(nodemat.node, annize.project.ScalarValueNode):
            value = nodemat.node.value
        else:
            return
        if nodemat.node.name:
            annize.flow.run_context.set_object_name(value, nodemat.node.name)
        nodemat.set_materialized_result([value])
        annize.flow.run_context.add_object(value)


class AssociateArgumentNodeBehavior(annize.project.materializer.behaviors.Behavior):

    def __init__(self, association: dict[annize.project.ArgumentNode, list[t.Any]]):
        self.__association = association

    @contextlib.contextmanager
    def node_context(self, nodemat):
        yield
        if isinstance(nodemat.node, annize.project.ArgumentNode) and nodemat.has_result:
            self.__association[nodemat.node] = nodemat.result
