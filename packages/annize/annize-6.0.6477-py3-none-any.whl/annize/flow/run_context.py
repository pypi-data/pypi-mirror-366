# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Run contexts. Typically used by the infrastructure in the course of the execution of an Annize project.

See also :py:class:`RunContext` and :py:func:`current`.
"""
import threading
import typing as t

import hallyd

import annize.data
import annize.i18n


class RunContext:
    """
    Holds data for a single execution of an Annize project (usually happening in a
    :py:class:`annize.flow.runner.Runner`).

    Beyond a few fixed data, like the root path of the Annize project configuration files, it stores every object that
    was created by definition in the Annize project configuration. Many parts of this API (e.g. many method names) use
    the term 'object' for all data items stored in a run context.

    Each of those objects has at least one name. This can be a "friendly name", i.e. a name that was explicitly
    specified in the project. If no name was specified, there will at least be an dynamically generated one, so every
    object is uniquely addressable by name. The dynamically generated names will differ between one project execution
    and another one, while friendly names are stable by nature.

    There are further ways to access stored data, which do not involve names. See this class' methods.

    For each object in the store, arbitrary metadata can be stored as well.

    See also :py:func:`current`.

    This run context needs to be entered (:code:`with`-block) during project execution.
    """

    _IS_TOPLEVEL_OBJECT__METADATA_KEY = annize.data.UniqueId("is_toplevel_object").processonly_long_str
    ANNIZE_CONFIG_ROOTPATH__NAME = annize.data.UniqueId("annize_config_rootpath").processonly_long_str

    def __init__(self):
        """
        Do not use directly.
        """
        self.__lock = threading.RLock()
        self.__objects_dict = {}
        self.__object_names = {}
        self.__object_metadata = {}
        self.__culture_fence = annize.i18n._CultureFence()
        self.__unspecified_culture = annize.i18n.UnspecifiedCulture()

    def __enter__(self):
        _contexts_stack.stack = stack = getattr(_contexts_stack, "stack", [])
        stack.append(self)
        self.__culture_fence.__enter__()
        self.__unspecified_culture.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__unspecified_culture.__exit__(exc_type, exc_val, exc_tb)
        self.__culture_fence.__exit__(exc_type, exc_val, exc_tb)
        _contexts_stack.stack.pop()
        if len(_contexts_stack.stack) == 0:
            delattr(_contexts_stack, "stack")

    def prepare(self, *, annize_config_rootpath: hallyd.fs.Path) -> None:
        """
        Prepare the execution.

        Needs to be called once, before the actual execution begins, in order to make some basic data available.

        :param annize_config_rootpath: The Annize project configuration root path.
        """
        self.set_object_name(annize_config_rootpath, RunContext.ANNIZE_CONFIG_ROOTPATH__NAME)

    def object_by_name(self, name: str, default: t.Any = None, *, create_nonexistent: bool = False) -> t.Any:
        """
        Return an object by one of its names (or a default value).

        See also :py:meth:`set_object_name`.

        :param name: An object name.
        :param default: The default value to return when no object exists with the given name.
        :param create_nonexistent: (If the default value is going to be returned because no object existed with the
                                   given name) Whether to store the default value in the data store with the given name,
                                   so it can be found later.
        """
        with self.__lock:
            result = self.__objects_dict.get(name, self)
            if result == self:
                result = default
                if create_nonexistent:
                    self.set_object_name(result, name)
            return result

    def object_names(self, obj: t.Any) -> list[str]:
        """
        Return all object names for a given object (with friendly names first).

        This method always returns a non-empty list. Even if the given object was not stored at all yet, it
        automatically gets added to the store implicitly.

        See also :py:meth:`set_object_name`.

        :param obj: The object.
        """
        with self.__lock:
            self.__object_raw_name(obj)
            return self.__object_names[id(obj)]

    def object_name(self, obj: t.Any) -> str:
        """
        Return one object name for a given object (preferably a friendly one).

        This method always returns a valid name. Even if the given object was not stored at all yet, it automatically
        gets added to the store implicitly.

        See also :py:meth:`set_object_name`.

        :param obj: The object.
        """
        return self.object_names(obj)[0]

    def set_object_name(self, obj: t.Any, name: str) -> None:
        """
        Assign a name to an object.

        All names assigned earlier remain valid as well.

        See also :py:meth:`object_by_name`, :py:meth:`object_names` and others.

        :param obj: The object.
        :param name: The new name.
        """
        self.__put_object(name, obj)

    def objects_by_type[T](self, obj_type: type[T], toplevel_only: bool = True) -> list[T]:
        """
        Return all stored objects that are instance of a given type.

        See also :py:meth:`add_object` and others.

        :param obj_type: The type.
        :param toplevel_only: Whether to return only objects that are defined on project level.
        """
        with self.__lock:
            result = []
            for obj in self.__objects_dict.values():
                if isinstance(obj, obj_type) and obj not in result:
                    result.append(obj)
        if toplevel_only:
            result = [obj for obj in result if self.is_toplevel_object(obj)]
        return result

    def add_object(self, obj: t.Any) -> str:
        """
        Add an object to the store and return its name.

        If the object already is the store, and already has a friendly name, this one is returned. So, in fact, this
        method has the same effect as :py:meth:`object_name`. It might just express your intent better than that one in
        some cases.

        See also :py:meth:`object_by_name`, :py:meth:`objects_by_type` and others.

        :param obj: The object to add.
        """
        return self.object_name(obj)

    def is_friendly_name(self, name: str) -> bool:
        """
        Returns whether the given name is a friendly one.

        :param name: The name to check.
        """
        return not name.startswith(annize.data.UniqueId("").processonly_long_str)

    def is_toplevel_object(self, obj: t.Any) -> bool:
        """
        Return whether a given object represents the definition of an object on the Annize project file root level
        (e.g. by the top level tags in .xml configuration files).

        :param obj: The object to check.
        """
        return self.object_metadata(obj, RunContext._IS_TOPLEVEL_OBJECT__METADATA_KEY, False)

    def mark_object_as_toplevel(self, obj: t.Any) -> None:
        """
        Mark an object as a toplevel one. See :py:meth:`is_toplevel_object`.

        :param obj: The object.
        """
        self.add_object(obj)
        return self.set_object_metadata(obj, RunContext._IS_TOPLEVEL_OBJECT__METADATA_KEY, True)

    # TODO use object metadata for names as well

    def object_metadata(self, obj: t.Any, key: str, default: t.Any = None) -> t.Any:
        """
        Return a piece of metadata for a given object (or a default value if there is no value by the given key).

        See also :py:meth:`set_object_metadata`.

        :param obj: The object.
        :param key: The metadata key.
        :param default: The default value.
        """
        return self.__object_metadata_dict(obj).get(key, default)

    def set_object_metadata(self, obj: t.Any, key: str, value: t.Any = None) -> None:
        """
        Store a piece of metadata for a given object.

        See also :py:meth:`object_metadata`.

        :param obj: The object.
        :param key: The metadata key.
        :param value: The metadata value to store for this object and key.
        """
        self.__object_metadata_dict(obj)[key] = value

    def __put_object(self, name: str, obj: t.Any) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name:
            raise ValueError("name must not be empty")
        with self.__lock:
            if self.__objects_dict.get(name, obj) != obj:
                raise ValueError(f"name '{name}' already assigned")
            self.__objects_dict[name] = obj
            object_name_list = self.__object_names[id(obj)] = self.__object_names.get(id(obj), [])
            if self.is_friendly_name(name):
                object_name_list.insert(0, name)
            else:
                object_name_list.append(name)

    def __object_raw_name(self, obj: t.Any) -> str:
        names = self.__object_names.get(id(obj), ())
        raw_names = [name for name in names if not self.is_friendly_name(name)]
        if raw_names:
            return raw_names[-1]
        raw_name = annize.data.UniqueId(str(id(obj))).long_str
        self.__put_object(raw_name, obj)
        return raw_name

    def __object_metadata_dict(self, obj: t.Any) -> dict[str, t.Any]:
        result = self.__object_metadata[id(obj)] = self.__object_metadata.get(id(obj), {})
        return result


_contexts_stack = threading.local()


def current() -> RunContext:
    """
    Return the current run context.

    Note: In most cases you do not need to use this function directly. See the other functions defined on module level.

    If there is no current run context (i.e. this function is called outside the execution of an Annize project),
    :py:class:`OutOfContextError` will be raised.
    """
    stack = getattr(_contexts_stack, "stack", None)
    if not stack:
        raise OutOfContextError()
    return stack[-1]


class OutOfContextError(TypeError):

    def __init__(self):
        super().__init__("There is no current Annize run context")


def object_by_name(name: str, default: t.Any = None, *, create_nonexistent: bool = False) -> t.Any:
    """
    Same as :py:meth:`RunContext.object_by_name` on the _current_ run context (:py:func:`current`).
    """
    return current().object_by_name(name, default, create_nonexistent=create_nonexistent)


def object_names(obj: t.Any) -> list[str]:
    """
    Same as :py:meth:`RunContext.object_names` on the _current_ run context (:py:func:`current`).
    """
    return current().object_names(obj)


def object_name(obj: t.Any) -> str:
    """
    Same as :py:meth:`RunContext.object_name` on the _current_ run context (:py:func:`current`).
    """
    return current().object_name(obj)


def set_object_name(obj: t.Any, name: str) -> None:
    """
    Same as :py:meth:`RunContext.set_object_name` on the _current_ run context (:py:func:`current`).
    """
    return current().set_object_name(obj, name)


def objects_by_type[T](obj_type: type[T], toplevel_only: bool = True) -> list[T]:
    """
    Same as :py:meth:`RunContext.objects_by_type` on the _current_ run context (:py:func:`current`).
    """
    return current().objects_by_type(obj_type, toplevel_only=toplevel_only)


def add_object(obj: t.Any) -> str:
    """
    Same as :py:meth:`RunContext.add_object` on the _current_ run context (:py:func:`current`).
    """
    return current().add_object(obj)


def is_friendly_name(name: str) -> bool:
    """
    Same as :py:meth:`RunContext.is_friendly_name` on the _current_ run context (:py:func:`current`).
    """
    return current().is_friendly_name(name)


def is_toplevel_object(obj: t.Any) -> bool:
    """
    Same as :py:meth:`RunContext.is_toplevel_object` on the _current_ run context (:py:func:`current`).
    """
    return current().is_toplevel_object(obj)


def object_metadata(obj: t.Any, key: str, default: t.Any = None) -> t.Any:
    """
    Same as :py:meth:`RunContext.object_metadata` on the _current_ run context (:py:func:`current`).
    """
    return current().object_metadata(obj, key, default)


def set_object_metadata(obj: t.Any, key: str, value: t.Any = None) -> None:
    """
    Same as :py:meth:`RunContext.set_object_metadata` on the _current_ run context (:py:func:`current`).
    """
    return current().set_object_metadata(obj, key, value)


# TODO xx xy how to cleanup whenever materializer loads features? contextvars?
