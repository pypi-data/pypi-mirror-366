# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Project inspector.

See :py:class:`Inspector`.
"""
import inspect
import typing as t

import annize.object.parameter_info
import annize.project.feature_loader


class Inspector:
    """
    Inspectors are used in order to get various additional metadata about parts of a project, which are useful e.g. for
    project configuration UIs.
    """

    class ArgumentMatchings:

        class ArgumentMatching:

            def __init__(self, arg_name: str, nodes: list[annize.project.ArgumentNode], allows_multiple_args: bool):
                self.__arg_name = arg_name or ""
                self.__nodes = nodes
                self.__allows_multiple_args = allows_multiple_args

            @property
            def argname(self) -> str:
                return self.__arg_name

            @property
            def allows_multiple_args(self) -> bool:
                return self.__allows_multiple_args

            @property
            def nodes(self) -> list[annize.project.ArgumentNode]:
                return self.__nodes

        def __init__(self, all_matchings: list["ArgumentMatching"]):
            self.__all = all_matchings

        def matching_by_argname(self, arg_name: str) -> "ArgumentMatching|None":
            for matching in self.__all:
                if matching.argname == arg_name:
                    return matching
            return None

        def all(self) -> list["ArgumentMatching"]:
            return list(self.__all)

    class TypeInfo:

        def __init__(self, feature: str|None, typename: str, ctype: type):
            self.__feature = feature
            self.__typename = typename
            self.__type = ctype

        @property
        def feature(self) -> str|None:
            return self.__feature

        @property
        def typename(self) -> str:
            return self.__typename

        @property
        def type(self) -> type:
            return self.__type

    def __init__(self, feature_loader: annize.project.feature_loader.FeatureLoader):
        self.__featureloader = feature_loader

    def match_arguments(self, node: annize.project.Node) -> ArgumentMatchings:
        result = None
        not_allows_multiple_args = set()
        if isinstance(node, annize.project.ObjectNode):
            featuremodule = self.__featureloader.load_feature(node.feature)
            if featuremodule:
                calltype = getattr(featuremodule, node.type_name, None)
                if calltype:
                    result = {}
                    argumentinfos = annize.object.parameter_info.type_parameter_infos(for_callable=calltype)
                    for argname, argumentinfo in argumentinfos.items():
                        result[argname] = []
                        if not argumentinfo.allows_multiple_args:
                            not_allows_multiple_args.add(argname)
                    result[""] = []
                    for childnode in node.children:
                        aname = getattr(childnode, "arg_name", "")#TODO
                        if not aname:
                            childnodetype = self.__get_node_materialtype(childnode)
                            if childnodetype:
                                ainf = [ain for ain, aiv in argumentinfos.items() if aiv.matches_inner_type(childnodetype)] + [""]  # TODO
                                aname = ainf[0]
                        alst = result[aname] = result.get(aname, [])
                        alst.append(childnode)
        if result is None:
            result = {"": node.children}
        return self.ArgumentMatchings([self.ArgumentMatchings.ArgumentMatching(argname, subnodes,
                                                                               argname not in not_allows_multiple_args)
                                       for argname, subnodes in result.items()])

    def match_node(self, node: annize.project.Node) -> ArgumentMatchings.ArgumentMatching|None:#TODO dedup match_arguments
        if isinstance(node.parent, annize.project.ObjectNode):
            featuremodule = self.__featureloader.load_feature(node.parent.feature)
            if featuremodule:
                calltype = getattr(featuremodule, node.parent.type_name, None)
                if calltype:
                    argumentinfos = annize.object.parameter_info.type_parameter_infos(for_callable=calltype)
                    nodetype = self.__get_node_materialtype(node)
                    nodeargname = getattr(node, "arg_name", "")  # TODO
                    for argname, argumentinfo in argumentinfos.items():
                        if (not nodeargname or nodeargname == argname) and argumentinfo.matches_type(nodetype):  # TODO shit  TODO blindly return the first one?!
                            return self.ArgumentMatchings.ArgumentMatching(argname, [node], argumentinfo.allows_multiple_args)
        return None

    def get_all_types(self) -> list["TypeInfo"]:
        result = []
        for valuetype in [str, int, float, bool]:  # TODO ?! more?! dynamic?!
            result.append(self.TypeInfo(None, valuetype.__name__, valuetype))
        for featurename in self.__featureloader.get_all_available_feature_names():
            feature = self.__featureloader.load_feature(featurename)
            for itemname in dir(feature):
                if not itemname.startswith("_"):
                    item = getattr(feature, itemname)
                    if inspect.isclass(item):
                        result.append(self.TypeInfo(featurename, itemname, item))
        return result

    def get_types_for_argument(self, node: annize.project.Node, argname: str) -> list["TypeInfo"]:
        argname = argname or ""
        if isinstance(node, annize.project.ObjectNode):
            featuremodule = self.__featureloader.load_feature(node.feature)
            if featuremodule:
                calltype = getattr(featuremodule, node.type_name, None)
                if calltype:
                    argumentinfos = annize.object.parameter_info.type_parameter_infos(for_callable=calltype)
                    argumentinfo = argumentinfos.get(argname)
                    if argumentinfo:
                        result = []
                        for rtype in self.get_all_types():
                            if argumentinfo.matches_inner_type(rtype.type):
                                result.append(rtype)
                        return result
        else:
            TODO
        return None  # TODO

    def get_project_node(self, node: annize.project.Node) -> annize.project.ProjectNode|None:
        while node and not isinstance(node, annize.project.ProjectNode):
            node = node.parent
        return node

    def get_node_by_name(self, subtree: annize.project.ProjectNode, name: str) -> annize.project.Node|None:
        if isinstance(subtree, annize.project.ArgumentNode) and subtree.name == name:
            return subtree
        for subtreechild in subtree.children:
            sresult = self.get_node_by_name(subtreechild, name)
            if sresult:
                return sresult
        return None

    def resolve_reference_node(self, node: annize.project.Node, *, deep: bool = True) -> annize.project.ArgumentNode|None:
        project_node = self.get_project_node(node)
        while isinstance(node, annize.project.ReferenceNode):
            oldnode, node = node, self.get_node_by_name(project_node, node.reference_key)
            if node is oldnode:
                node = None
            if not deep:
                break
        return node

    def __get_node_materialtype(self, node: annize.project.Node) -> type|None:
        node = self.resolve_reference_node(node)
        if isinstance(node, annize.project.ObjectNode):
            featuremodule = self.__featureloader.load_feature(node.feature)
            return getattr(featuremodule, node.type_name, None)
        return None
