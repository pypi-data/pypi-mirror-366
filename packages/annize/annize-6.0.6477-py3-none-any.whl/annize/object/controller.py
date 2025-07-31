# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
TODO.
"""
import dataclasses
import typing as t

import annize.object.parameter_info


class _CreateObjectHelper:

    @dataclasses.dataclass
    class ParameterConfig:

        parameter_name: str
        explicit_only: bool | None = None

        def with_updates(self, oconfig: "_CreateObjectHelper.ParameterConfig") -> "_CreateObjectHelper.ParameterConfig":
            return _CreateObjectHelper.ParameterConfig(self.parameter_name,
                                    self.explicit_only if (oconfig.explicit_only is None) else oconfig.explicit_only)

    @staticmethod
    def create_object(call_type, args: t.Iterable, kwargs: dict):
        argument_infos = annize.object.parameter_info.type_parameter_infos(for_callable=call_type)
        args, kwargs = _CreateObjectHelper.__convert_kwargs_from_string(argument_infos, args, kwargs)
        args, kwargs = _CreateObjectHelper.__fill_empty_lists(argument_infos, args, kwargs)
        args, kwargs = _CreateObjectHelper.__shift_args_to_kwargs(call_type, argument_infos, args, kwargs)
        args, kwargs = _CreateObjectHelper.__fill_unspecified_optionals(argument_infos, args, kwargs)
        if args:
            raise TypeError(f"unable to assign argument {args[0]!r} to one of {call_type}s keyword parameters (either"
                            f" because it is not compatible to any, or to more of them)")
        return call_type(*args, **kwargs)

    @staticmethod
    def __get_parameter_config(call_type: type, arg_name: str) -> ParameterConfig:
        result_config = _CreateObjectHelper.ParameterConfig(arg_name)
        for supertype in call_type.mro():
            super_type_ctor = getattr(supertype, "__init__", supertype)
            init_config = (getattr(super_type_ctor, "__annize__parameter_configs", None) or {}).get(arg_name)
            if init_config:
                result_config = result_config.with_updates(init_config)
        return result_config

    @staticmethod
    def __convert_kwargs_from_string(argument_infos, args, kwargs):
        kwargs = dict(kwargs)
        for param_name, param_type_info in argument_infos.items():
            param_original_value = kwargs.get(param_name, None)
            if param_type_info.is_constructable_from_string and isinstance(param_original_value, str):
                kwargs[param_name] = param_type_info.construct_from_string(param_original_value)
        return args, kwargs

    @staticmethod
    def __fill_empty_lists(argument_infos, args, kwargs):
        kwargs = dict(kwargs)
        for param_name, param_type_info in argument_infos.items():
            if param_type_info.allows_multiple_args and (param_name not in kwargs):
                kwargs[param_name] = []
        return args, kwargs

    @staticmethod
    def __shift_args_to_kwargs(call_type, argument_infos, args, kwargs):
        args_new = []
        for arg in args:
            matchingkws = _CreateObjectHelper.__determine_matching_keywords_for_arg(arg, call_type, argument_infos)
            if len(matchingkws) == 1:
                _CreateObjectHelper.__put_item_into_kwargs(arg, kwargs, matchingkws[0][0], matchingkws[0][1])
            else:
                args_new.append(arg)
        return args_new, kwargs

    @staticmethod
    def __fill_unspecified_optionals(argument_infos, args, kwargs):
        kwargs = dict(kwargs)
        for param_name, param_type_info in argument_infos.items():
            if param_type_info.is_optional and (param_name not in kwargs):
                kwargs[param_name] = None
        return args, kwargs

    @staticmethod
    def __determine_matching_keywords_for_arg(arg, call_type, argument_infos):
        result = []
        for param_name, param_type_info in argument_infos.items():
            if _CreateObjectHelper.__get_parameter_config(call_type, param_name).explicit_only:
                continue
            if (param_type_info.inner_type_info if param_type_info.allows_multiple_args else param_type_info).matches_object(arg):
                result.append((param_name, param_type_info))
        return result

    @staticmethod
    def __put_item_into_kwargs(arg, kwargs, kwarg_name, param_type_info):
        if param_type_info.allows_multiple_args:
            kwargs[kwarg_name].append(arg)
        else:
            if kwarg_name in kwargs:
                raise Exception("TODO already there")
            kwargs[kwarg_name] = arg


create_object = _CreateObjectHelper.create_object


class MultipleValuesForSingleArgumentError(TypeError):

    def __init__(self, argname: str):
        super().__init__(f"More than one value given for the single-value argument '{argname}'")
        self.argname = argname


# TODO review all (and usage in materializer)
