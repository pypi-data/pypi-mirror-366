# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Support for Annize configuration XML files.
"""
import contextlib
import dataclasses
import typing as t

import hallyd
import lxml.etree  # TODO dependency

import annize.project.file_formats


@annize.project.file_formats.register_file_format("xml")
class XmlFileFormat(annize.project.file_formats.FileFormat):

    @classmethod
    def parse_file(cls, path):
        parser = _XmlParser()
        return parser.parse_file(path)


class _XmlParser:

    class _Context:#TODO weg?!

        def __init__(self):
            self.__path = None
            self.__xnode = None
            self.__marshaler = None
            self.__consumed_in_errorreport = False

        @property
        def marshaler(self):#TODO weg?!
            return self.__marshaler

        @staticmethod
        def __nodeshort(xnode: lxml.etree.Element, maxlen=100):
            result = lxml.etree.tostring(xnode).decode().strip()
            result = result.replace("\r", "").replace("\n", "\u21b5")
            if len(result) > maxlen:
                result = result[maxlen-1] + "\u1801"
            return result

        def __str__(self):
            if self.__path:
                result = f"in {self.__path}"
                if self.__xnode is not None:
                    result += f" (around: {self.__nodeshort(self.__xnode)})"
            else:
                result = "in global scope"
            return result

        @contextlib.contextmanager
        def in_file(self, fpath: hallyd.fs.TInputPath, marshaler):
            self.__path = hallyd.fs.Path(fpath)
            self.__xnode = None
            self.__marshaler = marshaler
            try:
                yield
            finally:
                self.__path = None
                self.__xnode = None
                self.__marshaler = None

        @contextlib.contextmanager
        def in_node(self, xnode):
            xoldnode = self.__xnode
            self.__xnode = xnode
            try:
                yield
            except Exception as ex:
                if not self.__consumed_in_errorreport:
                    self.__consumed_in_errorreport = True
                    raise annize.project.ParserError(f"reading project definition failed {self}: {ex}") from ex
                raise
            finally:
                self.__xnode = xoldnode

    class _TagParts:

        def __init__(self, name, namespace: str = ""):
            if name.startswith("{"):
                if namespace:
                    raise annize.project.BadStructureError("namespace is specified via argument and inside the name,"
                                                           " which is conflicting")
                namespaceendidx = name.find("}")
                self.namespace, self.tagname = name[1:namespaceendidx], name[namespaceendidx + 1:]
            else:
                self.namespace, self.tagname = namespace, name

    def __init__(self):
        self.__context = self._Context()

    ATTRIBUTE_COMMAND_START = "~"
    ATTRIBUTE_COMMAND_END = "~"

    @classmethod
    def escape_attribute_string(cls, txt: str) -> str:
        if txt.startswith(cls.ATTRIBUTE_COMMAND_START) and txt.endswith(cls.ATTRIBUTE_COMMAND_END):
            return f"{cls.ATTRIBUTE_COMMAND_START}{txt}{cls.ATTRIBUTE_COMMAND_END}"

    @classmethod
    def __interpret_attribute_string(cls, txt: str) -> t.Tuple[bool, str]:
        is_command = False
        if txt.startswith(cls.ATTRIBUTE_COMMAND_START) and txt.endswith(cls.ATTRIBUTE_COMMAND_END):
            txt = txt[1:-1]
            if not txt.startswith(cls.ATTRIBUTE_COMMAND_START):
                is_command = True
        return is_command, txt

    @classmethod
    def __parse_attrib(cls, key: str, value: str) -> annize.project.Node:
        value_is_command, value = cls.__interpret_attribute_string(value)
        if value_is_command:
            if value == "False":
                value = False
            elif value == "True":
                value = True
            elif value.startswith("reference "):
                result = annize.project.ReferenceNode()
                result.reference_key = value[10:]
                result.arg_name = key
                return result
            else:
                raise annize.project.ParserError(f"invalid magic attribute value {value!r}")
        result = annize.project.ScalarValueNode()
        result.value = value
        result.arg_name = key
        return result

    def __parse_tag(self, node: annize.project.Node, argname, callname, feature, xnode):
        xresult = xnode
        if isinstance(node, annize.project.ObjectNode) and node.type_name == callname:
            if len(xnode) > 0:
                resultnode, xresult = self.__parse_child(node, xnode[0])
            else:
                resultnode = annize.project.ScalarValueNode()
                resultnode.value = xnode.text
            resultnode.arg_name = argname
        else:
            resultnode = annize.project.ObjectNode()
            resultnode.feature, resultnode.type_name = feature, callname
            cnode, xresult = self.__parse_child(resultnode, xnode)
            resultnode.append_child(cnode)
        return resultnode, xresult

    def __parse_child(
            self, node: annize.project.Node,
            xnode: lxml.etree.Element) -> t.Tuple[annize.project.Node, lxml.etree.Element]:
        xresult = xnode
        with self.__context.in_node(xnode):
            tagparts = self._TagParts(xnode.tag)
            namespace = tagparts.namespace or ""
            if namespace == "annize":
                if tagparts.tagname == "if_unavailable":
                    resultnode = annize.project.OnFeatureUnavailableNode()
                    resultnode.feature = xnode.attrib.get("feature", None)
                    resultnode.scope = xnode.attrib.get("scope", None)
                    resultnode.do = xnode.attrib.get("do", None)
                elif tagparts.tagname == "reference":
                    resultnode = annize.project.ReferenceNode()
                    resultnode.reference_key = xnode.attrib["name"]
                    resultnode.on_unresolvable = xnode.attrib.get("on_unresolvable", None)
                else:
                    raise annize.project.ParserError(f"invalid tag {tagparts.tagname!r}")
            elif namespace.startswith("annize:"):
                feature = namespace[7:]
                tagnamesegments = tagparts.tagname.split(".")
                if len(tagnamesegments) == 1:
                    resultnode = annize.project.ObjectNode()
                    resultnode.feature, resultnode.type_name = feature, tagnamesegments[0]
                elif len(tagnamesegments) == 2:
                    callname, argname = tagnamesegments
                    resultnode, xresult = self.__parse_tag(node, argname, callname, feature, xnode)
                else:
                    raise annize.project.BadStructureError(f"Invalid argument '{tagparts.tagname}'")
                for attribkey, attribvalue in xnode.attrib.items():
                    if attribkey == "{annize}name":
                        resultnode.name = attribvalue
                    elif attribkey == "{annize}append_to":
                        resultnode.append_to = attribvalue
                    else:
                        xinode = self.__parse_attrib(attribkey, attribvalue)
                        self.__context.marshaler.add_element_attr(xinode, xnode, attribkey)
                        resultnode.append_child(xinode)
            else:
                raise annize.project.BadStructureError(f"invalid namespace {namespace!r}" if namespace
                                                       else "missing namespace")
            self.__context.marshaler.add_element(resultnode, xnode)
            return resultnode, xresult

    def __parse_children(self, node: annize.project.Node, xparent: lxml.etree.Element):
        for xnode in xparent:
            if xnode.tag is lxml.etree.Comment:
                continue#TODO
            childnode, xchildinnernode = self.__parse_child(node, xnode)
            if childnode:
                node.append_child(childnode)
                self.__parse_children(childnode, xchildinnernode)

    def parse_file(self, fpath: hallyd.fs.TInputPath) -> annize.project.FileNode:
        marshaler = Marshaler()
        with self.__context.in_file(fpath, marshaler):
            result = annize.project.FileNode(fpath, marshaler)
            xtree = lxml.etree.parse(fpath)
            marshaler.add_element_tree(result, xtree)
            with self.__context.in_node(xtree.getroot()):
                self.__parse_children(result, xtree.getroot())
            return result


class Marshaler(annize.project.file_formats.FileFormat.Marshaler):  # TODO  other package structure

    @dataclasses.dataclass
    class XmlDocumentLocation:
        element: lxml.etree.Element
        attr_name: str = ""

    def __init__(self):
        super().__init__()
        self.__elements = {}
        self.__elementtrees = {}

    def add_change(self, change):#TODO review # TODO this is all not really correct
        print("TODO mm", change)
        targetxmllocation = self.__elements[change.target_node]
        if isinstance(change, annize.project.Node.ChildAddedEvent):
            childxmllocation = self.__elements.get(change.child_node)
            if not childxmllocation:
                feature = change.child_node.feature  # TODO
                type_name = change.child_node.type_name
                TODO = lxml.etree.Element(f"{{annize:{feature}}}{type_name}")
                childxmllocation = self.XmlDocumentLocation(TODO)
            targetxmllocation.element.insert(change.child_position, childxmllocation.element)
        elif isinstance(change, annize.project.Node.ChildRemovedEvent):
            childxmllocation = self.__elements[change.child_node]
            targetxmllocation.element.remove(childxmllocation.element)
        elif isinstance(change, annize.project.Node.PropertyChangedEvent):
            print("TODO tff", change.target_node, change.property_name, change.new_value, targetxmllocation)
            is_argument_node = isinstance(change.target_node, annize.project.ArgumentNode)
            is_on_feature_unavailable_node = isinstance(change.target_node, annize.project.OnFeatureUnavailableNode)
            is_reference_node = isinstance(change.target_node, annize.project.ReferenceNode)
            is_scalar_value_node = isinstance(change.target_node, annize.project.ScalarValueNode)
            is_scopable_block_node = isinstance(change.target_node, annize.project.BlockNodeWithScope)
            if is_argument_node and change.property_name == "name":
                targetxmllocation.element.attrib["{annize}name"] = change.new_value
            elif is_argument_node and change.property_name == "append_to":
                targetxmllocation.element.attrib["{annize}append_to"] = change.new_value
            elif is_on_feature_unavailable_node and change.property_name == "do":
                targetxmllocation.element.attrib["do"] = change.new_value
            elif is_on_feature_unavailable_node and change.property_name == "feature":
                targetxmllocation.element.attrib["feature"] = change.new_value
            elif is_reference_node and change.property_name == "reference_key":
                targetxmllocation.element.attrib["name"] = change.new_value
            elif is_scalar_value_node and change.property_name == "value":
                targetxmllocation.element.attrib[targetxmllocation.attr_name] = change.new_value
            elif is_scopable_block_node and change.property_name == "scope":
                targetxmllocation.element.attrib["scope"] = change.new_value
            else:
                raise Exception("TODO")
        else:
            raise Exception("TODO")

    def add_element(self, node: "annize.project.Node", xelem: lxml.etree.Element):
        self.__elements[node] = self.XmlDocumentLocation(xelem)

    def add_element_attr(self, node: "annize.project.Node", xelem: lxml.etree.Element, attrname: str):
        self.__elements[node] = self.XmlDocumentLocation(xelem, attrname)

    def add_element_tree(self, node: "annize.project.Node", xtree: lxml.etree.ElementTree):
        self.__elements[node] = self.XmlDocumentLocation(xtree.getroot())
        self.__elementtrees[node] = xtree

    def save_filenode_to_file(self, node: "annize.project.FileNode"):  # TODO in base class
        xtree = self.__elementtrees[node]
        xtree.write(node.path, encoding="UTF-8")

# TODO raise errors on unexpected attributes in <a:...> tags
