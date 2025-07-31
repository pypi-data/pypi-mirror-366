# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
TODO.
"""
import importlib
import inspect
import sys
import types
import typing as t

import annize.i18n


class ParameterInfo:  # TODO refactor this and subclasses

    def __init__(self, name: str, resolved_type: type|None, is_optional: bool,
                 construct_from_string_func: t.Callable[[str], t.Any]|None):
        self.__name = name
        self.__resolved_type = resolved_type
        self.__is_optional = is_optional
        self.__construct_from_string_func = construct_from_string_func

    @property
    def name(self) -> str:
        return self.__name

    @property
    def resolved_type(self) -> type|None:
        return self.__resolved_type

    def matches_object(self, obj: object) -> bool:
        return self.matches_type(type(obj))

    def matches_type(self, type_: type) -> bool:
        return (self.resolved_type and issubclass(type_, self.resolved_type)) \
               or (type_ is str and self.is_constructable_from_string)  # TODO good or not?

    def matches_inner_type(self, type_: type) -> bool:#TODO
        if inner_type_info := self.inner_type_info:
            return inner_type_info.matches_type(type_)
        else:
            return self.matches_type(type_)

    @property
    def is_optional(self) -> bool:
        return self.__is_optional

    @property
    def inner_type_info(self) -> "ParameterInfo|None":
        return None

    @property
    def allows_multiple_args(self) -> bool:
        return False

    @property
    def is_constructable_from_string(self) -> bool:
        return self.__construct_from_string_func is not None

    def construct_from_string(self, s: str) -> t.Any:  # TODO review
        return self.__construct_from_string_func(s)


class ListParameterInfo(ParameterInfo):

    def __init__(self, name: str, is_optional: bool, innertypeinfo):
        super().__init__(name, list, is_optional, None)
        self.__inner = innertypeinfo

    @property
    def allows_multiple_args(self):
        return True

    @property
    def inner_type_info(self):
        return self.__inner


class UnionParameterInfo(ParameterInfo):

    def __init__(self, name: str, is_optional: bool, union_member_type_infos):
        super().__init__(name, None, is_optional, None)
        self.__union_member_type_infos = union_member_type_infos

    @property
    def resolved_type(self):
        return None

    def matches_object(self, obj):
        return any(union_member_type_info.matches_object(obj)
                   for union_member_type_info in self.__union_member_type_infos)


def _get_type_info(for_type, as_optional: bool = False) -> ParameterInfo:
    # TODO nicer code
    if isinstance(for_type, (t._GenericAlias, types.GenericAlias, types.UnionType)):
        if getattr(for_type, "__origin__", None) is t.Union or isinstance(for_type, types.UnionType):
            ftargs = getattr(for_type, "__args__", ())
            ftrealargs = [ftarg for ftarg in ftargs if ftarg is not type(None)]
            is_optional = len(ftrealargs) < len(ftargs)
            ftrealargs = ftrealargs or [object]
            if len(ftrealargs) == 1:
                return _get_type_info(ftrealargs[0], is_optional)
            return UnionParameterInfo(str(for_type), is_optional, [_get_type_info(ftt) for ftt in ftrealargs])
        return ListParameterInfo(str(for_type), as_optional, _get_type_info(for_type.__args__[0]))
    if isinstance(for_type, t.ForwardRef):
        for_type = for_type.__forward_arg__
    if isinstance(for_type, str):
        def findmodule(typename):
            for i in reversed(range(len(typename))):
                if typename[i] == ".":
                    modulename = typename[:i]
                    importlib.import_module(modulename)
                    if modulename in sys.modules:
                        return sys.modules[modulename], typename[i + 1:]
            return None, None
        containingmodule, shorttypename = findmodule(for_type)
        if shorttypename:
            for_type = eval(shorttypename, containingmodule.__dict__)  # pylint: disable=eval-used
        constructfromstringfct = None
    else:
        constructfromstringfct = for_type
    if for_type is annize.i18n.TrStr:  # TODO externalize?!
        constructfromstringfct = annize.i18n.to_trstr
    return ParameterInfo(for_type.__name__, for_type, as_optional, constructfromstringfct)


def type_parameter_infos(*, for_callable: t.Callable) -> dict[str, ParameterInfo]:
    result = {}
    mro = for_callable.mro() if isinstance(for_callable, type) else [for_callable]
    fargsspec = inspect.getfullargspec(for_callable)
    for paramname in fargsspec.kwonlyargs:
        paramtype = None
        for mrocallablefc in mro:
            for callablefc in [getattr(mrocallablefc, "__init__", None), getattr(mrocallablefc, "__new__", None)]:
                paramtype = getattr(callablefc, "__annotations__", {}).get(paramname, None)
                if paramtype:
                    break
            if paramtype:
                result[paramname] = _get_type_info(paramtype)
                break
    if fargsspec.varkw and isinstance(for_callable, type):
        for superclass in inspect.getclasstree([for_callable], unique=True)[-1][0][1]:
            for sakey, saval in type_parameter_infos(for_callable=superclass).items():
                if sakey not in result:
                    result[sakey] = saval
    for akwarg in fargsspec.kwonlyargs:
        if akwarg not in result:
            result[akwarg] = _get_type_info(object)
    return result
