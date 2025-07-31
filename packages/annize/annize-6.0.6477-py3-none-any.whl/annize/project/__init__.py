# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize projects.

See :py:class:`Project`, :py:class:`Node` and also the submodules.
"""
import abc
import copy
import enum
import sys
import typing as t

import hallyd

import annize.project.file_formats
import annize.project.loader


class Project:
    """
    An Annize project.

    The configuration structure is available in :py:attr:`node`.
    """

    def __init__(self, node: "ProjectNode", annize_config_rootpath: hallyd.fs.TInputPath):
        """
        Do not use directly.

        Load a project with :py:meth:`load` or create a fresh project with :py:meth:`create_new`. Save changes with
        :py:meth:`save`.
        """
        self.__node = node
        self.__annize_config_rootpath = hallyd.fs.Path(annize_config_rootpath)

    @property
    def node(self) -> "ProjectNode":
        """
        The project node.

        This contains the entire configuration structure of this project.
        """
        return self.__node

    @property
    def annize_config_rootpath(self) -> hallyd.fs.Path:
        """
        The "config root path" of this Annize project.

        This is usually not the same as the project's "root path", but a subdirectory like ':code:`-meta`' inside it.
        """
        return self.__annize_config_rootpath

    @staticmethod
    def load(project_path: hallyd.fs.TInputPath) -> "Project|None":
        """
        Load a project from disk. Return :code:`None` if the given path does not point into an Annize project.

        :param project_path: A path somewhere inside the project to be opened.
        """
        return annize.project.loader.load_project(str(project_path))

    def save(self):
        """
        Save the current state of the project back to disk.
        """
        self.__node.save()

    @staticmethod
    def create_new(project_root_path: hallyd.fs.TInputPath, subdirectory_name: str = "-meta") -> "Project":
        """
        Create a new Annize project.

        This will create an initial version of the Annize project configuration on disk as well.

        :param project_root_path: The project root path.
        :param subdirectory_name: The subdirectory name where to store the Annize configuration files inside the project
                                  root directory. This is not arbitrary but must be one of the well known ones!
        """
        project_root_path = hallyd.fs.Path(project_root_path)
        if annize.project.loader.find_project_annize_config_root_file(project_root_path):
            raise RuntimeError("Annize projects must not contain other Annize projects")
        # TODO check valid subdirectory_name
        annize_config_root_directory = hallyd.fs.Path(project_root_path, subdirectory_name)
        annize_config_root_directory.mkdir()
        annize_config_root_directory("project.xml").write_text(
            f'<a:project xmlns:a="annize" xmlns="annize:base">\n'
            f'    <Data project_name="{project_root_path.name}"/>\n'
            f'</a:project>\n')
        return Project.load(project_root_path)


class Node(abc.ABC):
    """
    Nodes are the building blocks of a project.

    They exist in a serialized way in the project files (usually xml), and when the project is loaded to memory (see
    :py:mod:`annize.project.loader`) they are represented by a structure of :code:`Node` instances.

    Each :code:`Node` has various features (see methods and properties of this class), e.g. it can be observed for
    changes. Each node can also have children. This is just a base class for more specific node types, though. See also
    its subclasses in the same module.

    The most relevant subclass in many regards is :py:class:`ObjectNode`.
    """

    class ChangeEvent:
        """
        Base class for events on a :py:class:`Node`. See subclasses and :py:meth:`Node.add_change_handler`.
        """

        def __init__(self, target_node: "Node"):
            self.__target_node = target_node

        @property
        def target_node(self) -> "Node":
            """
            The target node this event is about.
            """
            return self.__target_node

    class ChildrenListChangeEvent(ChangeEvent):
        """
        Base class for events on a :py:class:`Node` that are about changes on the list of children. See subclasses.
        """

        def __init__(self, target_node: "Node", child_node: "Node", child_position: int):
            super().__init__(target_node)
            self.__child_node = child_node
            self.__child_position = child_position

        @property
        def child_node(self) -> "Node":
            """
            The child node this event is about.
            """
            return self.__child_node

        @property
        def child_position(self) -> int:
            """
            The position of the child node in the list of children.
            """
            return self.__child_position

    class ChildAddedEvent(ChildrenListChangeEvent):
        """
        Node event that occurs when a child node was added.
        """

    class ChildRemovedEvent(ChildrenListChangeEvent):
        """
        Node event that occurs when a child node was removed.
        """

    class PropertyChangedEvent(ChangeEvent):
        """
        Node event that occurs when a property of a node was changed.
        """

        def __init__(self, target_node: "Node", property_name: str, old_value: t.Any, new_value: t.Any):
            super().__init__(target_node)
            self.__property_name = property_name
            self.__old_value = old_value
            self.__new_value = new_value

        @property
        def property_name(self) -> str:
            """
            The property name.
            """
            return self.__property_name

        @property
        def old_value(self) -> t.Any:
            """
            The old property value.
            """
            return self.__old_value

        @property
        def new_value(self) -> t.Any:
            """
            The new property value.
            """
            return self.__new_value

    def __init__(self):
        self.__parent = None
        self.__children = []
        self.__changed_handlers = []

    def add_change_handler(self, handler: t.Callable[[ChangeEvent], None], *, also_watch_children: bool):
        """
        Add a function that handles changes on this node.

        See also :py:meth:`remove_change_handler`.

        :param handler: The handler function to add.
        :param also_watch_children: Whether this function shall also observe this node's children.
        """
        self.__changed_handlers.append((handler, also_watch_children))

    def remove_change_handler(self, handler: t.Callable[[ChangeEvent], None]):
        """
        Remove a change handler function that was added by :py:meth:`add_change_handler` earlier.

        If that function was added multiple times, it will remove all of them. If the function was not added, this will
        do nothing.

        :param handler: The handler function to remove.
        """
        for i, handler_tuple in reversed(list(enumerate(self.__changed_handlers))):
            if handler_tuple[0] == handler:
                self.__changed_handlers.pop(i)

    def __changed__helpers(self, event: ChangeEvent):
        for handler, also_watch_children in tuple(self.__changed_handlers):
            if also_watch_children or (self is event.target_node):
                handler(event)
        if self.parent:
            self.parent.__changed__helpers(event)

    def _changed__child_added(self, child_node: "Node", child_position: int):
        self.__changed__helpers(self.ChildAddedEvent(child_node.parent, child_node, child_position))

    def _changed__child_removed(self, child_node: "Node", child_position: int):
        self.__changed__helpers(self.ChildRemovedEvent(child_node.parent, child_node, child_position))

    def _changed__property_changed(self, node: "Node", property_name: str, old_value: t.Any, new_value: t.Any):
        if old_value != new_value:
            self.__changed__helpers(self.PropertyChangedEvent(node, property_name, old_value, new_value))

    @property
    def parent(self) -> "Node|None":
        """
        This node's parent node.
        """
        return self.__parent

    @property
    def children(self) -> t.Iterable["Node"]:
        """
        This node's child nodes.
        """
        return tuple(self.__children)

    def insert_child(self, i: int, node: "Node") -> None:
        """
        Insert a new child node.

        :param i: The position.
        :param node: The node to insert.
        """
        if node.__parent:
            raise BadStructureError("tried to add a child node that already has a parent")
        for allowedchildtype in self._allowed_child_types():
            if isinstance(node, allowedchildtype):
                break
        else:
            raise BadStructureError(f"unexpected node {node!r}")
        node.__parent = self
        self.__children.insert(i, node)
        self._changed__child_added(node, i)

    def append_child(self, node: "Node") -> None:
        """
        Append a new child node.

        :param node: The node to append.
        """
        self.insert_child(len(self.__children), node)

    def remove_child(self, node: "Node") -> None:
        """
        Remove a child node.

        If that node is not a child node, it raises a :code:`ValueError`.

        :param node: The node to remove.
        """
        index = self.__children.index(node)
        self.__children.pop(index)
        self._changed__child_removed(node, index)
        node.__parent = None

    @classmethod
    @abc.abstractmethod
    def _allowed_child_types(cls) -> t.Iterable[type["Node"]]:
        """
        Return a list of node types that this node type allows to have as child nodes.
        """

    def clone(self, with_children: bool = True, with_marshalers: bool = False) -> "Node":  # TODO refactor TODO move to external service?!
        result = copy.copy(self)
        if not with_marshalers and isinstance(result, FileNode):
            class NullMarshaler:#TODO
                def add_change(self, *_):
                    pass
            result.marshaler = NullMarshaler()
        if isinstance(result, ProjectNode):
            result._ProjectNode__changes = [] #TODO
        result.__parent = None
        result.__children = []
        result.__changed_handlers = []
        if with_children:
            for child in self.children:
                result.append_child(child.clone())
        return result

    def description(self, *, with_children: bool = True, multiline: bool = True) -> str:
        return self.__description(0, with_children, multiline)

    def __description(self, indent: int, with_children: bool, multiline: bool) -> str:
        linesep = "\n" if multiline else "; "
        indentstr = indent * "  "
        details = tuple(self._str_helper())
        result = f"{indentstr}- {type(self).__name__}: {details[0] if details else ''}{linesep}"
        for detail in details[1:]:
            result += f"{indentstr}  {detail}{linesep}"
        if with_children:
            for child in self.children:
                result += child.__description(indent+1, with_children, multiline)
        return result

    def __str__(self):
        return self.description(with_children=False, multiline=False)

    @abc.abstractmethod
    def _str_helper(self) -> t.Iterable[str]:
        return []


class ProjectNode(Node):
    """
    An Annize project root node.

    Each project has exactly one root node. It has no parent. Its children are the Annize project configuration files.
    It has no direct serialized representation (or, one could argue, it is the directory that contains these files).
    """

    def __init__(self):
        super().__init__()
        self.__changes = []
        self.__first_unsaved_change_index = 0  #TODO needed ?!

    def save(self):
        """
        Store the current state to the Annize project configuration files.
        """
        for filenode in self.children:
            filenode.marshaler.save_filenode_to_file(filenode)

    def insert_child(self, i, node):
        node.add_change_handler(self.__changed_handler, also_watch_children=True)  # TODO
        return super().insert_child(i, node)

    def __changed_handler(self, event: "Node.ChangeEvent"):
        filenode = event.target_node
        while not isinstance(filenode, FileNode):
            filenode = filenode.parent
        self.__changes.append(event)
        filenode.marshaler.add_change(event)

    def get_changes(self, *, since: int = 0, until: int = sys.maxsize) -> list["Node.ChangeEvent"]:
        """
        Return all changes that happened to the project, since the moment of loading it or any later point in time, and
        until now or any earlier point in time.

        All timestamp arguments are based on a virtual clock (which basically increases by 1 for each change).
        See TODO.

        :param since: The timestamp where to start with returning changes (inclusive).
        :param until: The timestamp where to stop with return changes (non-inclusive).
        """
        return self.__compacted_changelist(self.__changes[since:until])

    @staticmethod
    def __compacted_changelist(events: list["Node.ChangeEvent"]) -> list["Node.ChangeEvent|None"]:
        def inverse_of(xx, yy):        #TODO
            if isinstance(xx, Node.ChildAddedEvent):
                return isinstance(yy, Node.ChildRemovedEvent) and (xx.child_node is yy.child_node)
            elif isinstance(xx, Node.ChildRemovedEvent):
                return isinstance(yy, Node.ChildAddedEvent) and (xx.child_node is yy.child_node)
            else:
                return isinstance(yy, Node.PropertyChangedEvent) and "TODO"
        result = []
        ilast = -1
        was_effective = False
        for ievent, event in enumerate(events):
            if not event:
                result.append(None)
            elif (ilast >= 0) and inverse_of(event, events[ilast]):
                result[ilast] = None
                result.append(None)
                ilast = -1
                was_effective = True
            else:
                result.append(event)
                ilast = ievent
        return ProjectNode.__compacted_changelist(result) if was_effective else result

    def undo_changes(self, since: int) -> None:
        """
        Undo all changes that happened to the project since a given point in time.

        :param since: The timestamp where to start with undoing changes (inclusive).
        """
        for event in reversed(self.get_changes(since=since)):
            if not event:
                continue
            if isinstance(event, Node.ChildAddedEvent):
                event.target_node.remove_child(event.child_node)
            elif isinstance(event, Node.ChildRemovedEvent):
                event.target_node.insert_child(event.child_position, event.child_node)
            elif isinstance(event, Node.PropertyChangedEvent):
                setattr(event.target_node, event.property_name, event.old_value)
            else:
                raise Exception("TODO")

    @staticmethod
    def load(path: hallyd.fs.TInputPath) -> "ProjectNode":
        return annize.project.file_formats.parse(path)

    @classmethod
    def _allowed_child_types(cls):
        return [FileNode]

    def _str_helper(self):
        return ()


class FileNode(Node):
    """
    An Annize project file node.

    Each project has one file node per configuration file. They are the children of the :py:class:`ProjectNode`. The
    children of a file node are mostly of type :py:class:`ObjectNode`, but can also be different ones.
    """

    def __init__(self, path: hallyd.fs.TInputPath, marshaler: "TODO"):
        super().__init__()
        self.__path = hallyd.fs.Path(path)
        self.__marshaler = marshaler

    @property
    def path(self) -> hallyd.fs.Path:
        """
        The file path.
        """
        return self.__path

    @property
    def marshaler(self) -> "TODO":
        return self.__marshaler

    @marshaler.setter
    def marshaler(self, marshaler):  # TODO
        self.__marshaler = marshaler

    def _str_helper(self):
        return [str(self.path)]

    @classmethod
    def _allowed_child_types(cls):
        return [ObjectNode, BlockNode]


class ArgumentNode(Node, abc.ABC):
    """
    Base class for nodes that can be used as an argument, usually in an :py:class:`ObjectNode`.

    See subclasses.
    """

    def __init__(self):
        super().__init__()
        self.__arg_name = None
        self.__name = None
        self.__append_to = None

    @property
    def name(self) -> str|None:
        """
        The name of this argument node.

        Names are used for a few purposes (the documentation will mention that where it is important), but primarily
        you can refer to a named argument with a :py:class:`ReferenceNode` and you can use it for :py:attr:`append_to`.
        """
        return self.__name

    @name.setter
    def name(self, _: str|None):
        old_name = self.__name
        self.__name = _
        self._changed__property_changed(self, "name", old_name, _)

    @property
    def append_to(self) -> str|None:
        """
        The name of another argument node where this argument node gets appended to its children at runtime.

        This essentially makes this argument node appear twice at runtime. It will also be in the place where it was
        defined; just a reference to that argument is created as a result.
        """
        return self.__append_to

    @append_to.setter
    def append_to(self, _: str|None):
        old_append_to = self.__append_to
        self.__append_to = _
        self._changed__property_changed(self, "append_to", old_append_to, _)

    @property
    def arg_name(self) -> str|None:
        """
        The argument name where this argument is associated to in the parent object.

        Valid argument names depend on the type of object that the parent is representing.
        """
        return self.__arg_name

    @arg_name.setter
    def arg_name(self, _: str|None):
        _ = _ or None
        old_arg_name = self.__arg_name
        self.__arg_name = _
        self._changed__property_changed(self, "arg_name", old_arg_name, _)

    def _str_helper(self):
        return ([f"arg_name: {self.arg_name}"] if self.arg_name else []) + \
               ([f"append_to: {self.append_to}"] if self.append_to else [])


class ObjectNode(ArgumentNode):
    """
    An Annize project object node.

    In a typical Annize project, most nodes are object nodes. Most structure in their project files represent them
    (usually the tags in xml files). All the other node types are basically related to containing object nodes
    (like file nodes or the project root node) or have other support purposes.

    Children are mostly other object nodes, :py:class:`ScalarValueNode` or :py:class:`ReferenceNode`. They are
    associated to a particular parameter name (of the object type) by their :py:attr:`ArgumentNode.arg_name`.
    """

    def __init__(self):
        super().__init__()
        self.__callee = None
        self.__feature = None

    @property
    def type_name(self) -> str:
        """
        The name of the type of this object.
        """
        return self.__callee

    @type_name.setter
    def type_name(self, _: str):
        old_callee = self.__callee
        self.__callee = _
        self._changed__property_changed(self, "type_name", old_callee, _)

    @property
    def feature(self) -> str:
        """
        The Annize feature name that provides this object.
        """
        return self.__feature

    @feature.setter
    def feature(self, _: str):
        old_feature = self.__feature
        self.__feature = _
        self._changed__property_changed(self, "feature", old_feature, _)

    def _str_helper(self):
        return [f"{self.feature} :: {self.type_name}", *super()._str_helper()]

    @classmethod
    def _allowed_child_types(cls):
        return [ArgumentNode, BlockNode]


class ScalarValueNode(ArgumentNode):
    """
    An Annize project scalar value node.

    It represents a fixed string value.
    """

    def __init__(self):
        super().__init__()
        self.__value = None

    @property
    def value(self) -> str:
        """
        The string that this node represents.
        """
        return self.__value

    @value.setter
    def value(self, _: str):
        old_value = self.__value
        self.__value = _
        self._changed__property_changed(self, "value", old_value, _)

    def _str_helper(self):
        return [self.__shorten(self.value), *super()._str_helper()]

    @staticmethod
    def __shorten(obj: t.Any, maxlen: int = 100) -> str:
        result = str(obj).replace("\r", "").replace("\n", "\u21b5")
        if len(result) > maxlen:
            result = result[:maxlen-1] + "\u1801"
        return result

    @classmethod
    def _allowed_child_types(cls):
        return []


class ReferenceNode(ArgumentNode):
    """
    A reference node.

    This node represents a reference to another node (by its :py:attr:`ArgumentNode.name`)
    """

    class OnUnresolvableAction(enum.Enum):
        FAIL = "fail"
        SKIP = "skip"

    def __init__(self):
        super().__init__()
        self.__reference_key = None
        self.__on_unresolvable = None

    @property
    def reference_key(self) -> str:
        """
        The name of the node this node references to.
        """
        return self.__reference_key

    @reference_key.setter
    def reference_key(self, _: str):
        old_reference_key = self.__reference_key
        self.__reference_key = _
        self._changed__property_changed(self, "reference_key", old_reference_key, _)

    @property
    def on_unresolvable(self) -> OnUnresolvableAction:  # TODO ?!?!
        return self.OnUnresolvableAction(self.__on_unresolvable or self.OnUnresolvableAction.FAIL.value)

    @on_unresolvable.setter
    def on_unresolvable(self, _: OnUnresolvableAction):   # TODO weird shit
        str(_)  # checks if valid   # TODO weird shit
        _ = getattr(_, "value", _)
        old_on_onresolvable = self.__on_unresolvable
        self.__on_unresolvable = _
        self._changed__property_changed(self, "on_unresolvable", old_on_onresolvable, _)

    def _str_helper(self):
        return [f"name {self.reference_key}", *super()._str_helper()]

    @classmethod
    def _allowed_child_types(cls):
        return []


class BlockNode(Node):
    """
    A block node without any own behavior.

    The purpose of that block differs for particular subclass.
    """

    def _str_helper(self):
        return ()

    @classmethod
    def _allowed_child_types(cls):
        return [Node]


class BlockNodeWithScope(BlockNode):
    """
    Base class for a block node with an additional scope definition.

    The purpose of the block and the scope definition depend on the particular subclass.
    """

    class Scope(enum.Enum):
        BLOCK = "block"
        FILE = "file"
        PROJECT = "project"

    def __init__(self):
        super().__init__()
        self.__scope = None

    def _str_helper(self):
        return [f"{self.scope.value} scope", *super()._str_helper()]

    @property
    def scope(self) -> Scope:
        """
        The scope of this block.
        """
        return self.Scope(self.__scope or self.Scope.BLOCK.value)

    @scope.setter
    def scope(self, _: Scope):   # TODO weird shit
        str(self.scope)  # checks if valid   # TODO weird shit
        _ = getattr(_, "value", _)
        old_scope = self.__scope
        self.__scope = _
        self._changed__property_changed(self, "scope", old_scope, _)


class OnFeatureUnavailableNode(BlockNodeWithScope):  # TODO also have an OnErrorDuringCreationNode ?!
    """
    An Annize project on-Feature-unavailable definition node.

    They control how Annize behaves when the project configuration refers to a Feature that is not available.

    The :py:attr:`scope` defines whether this rule applies only for the block, for the entire file that contains it, or
    for the entire project, while :py:attr:`do` defines if and how much gets ignored when the specified Feature is not
    available.
    """

    class Action(enum.Enum):
        FAIL = "fail"
        SKIP_BLOCK = "skip_block"
        SKIP_NODE = "skip_node"

    def __init__(self):
        super().__init__()
        self.__feature = None
        self.__do = None

    def _str_helper(self):
        return [f"{self.do.value} for Feature {self.feature}", *super()._str_helper()]

    @property
    def feature(self) -> "str":
        """
        The name of the Feature that gets checked by this node. Empty string or :code:`*` (the default) means all
        features.
        """
        return self.__feature or "*"

    @feature.setter
    def feature(self, _: "str"):
        old_feature = self.__feature
        self.__feature = _
        self._changed__property_changed(self, "feature", old_feature, _)

    @property
    def do(self) -> Action:
        """
        The action when the specified Feature is not available.
        """
        return self.Action(self.__do or self.Action.FAIL.value)

    @do.setter
    def do(self, _: Action):   # TODO weird shit
        str(self.do)  # checks if valid   # TODO weird shit
        _ = getattr(_, "value", _)
        old_do = self.__do
        self.__do = _
        self._changed__property_changed(self, "do", old_do, _)


class FeatureUnavailableError(ModuleNotFoundError):

    def __init__(self, feature_name: str):
        super().__init__(f"no Annize Feature named {feature_name!r}")
        self.feature_name = feature_name


class BadStructureError(ValueError):

    def __init__(self, message: str):
        super().__init__(f"bad project structure: {message}")


class MaterializerError(TypeError):

    def __init__(self, message: str):
        super().__init__(f"unable to materialize project structure: {message}")


class ParserError(ValueError):
    """
    Parsing error like bad input xml.
    """

    def __init__(self, message: str):
        super().__init__(f"unable to parse project definition: {message}")


class UnresolvableReferenceError(MaterializerError):

    def __init__(self, reference_key: str):
        super().__init__(f"reference {reference_key!r} is unresolvable")
        self.reference_key = reference_key
        self.retry_can_help = True
