# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Handling of Annize objects.

There is no particular subclass that all Annize objects inherit from! Annize objects can be of arbitrary types.

There are some decorators for optional configuration and finetuning of Annize objects' methods and attributes here.

In submodules, there are routines for object and object type handling, internally used by the infrastructure.
"""
import annize.object.controller


def explicit_only(arg_name: str):
    def decor(func):
        param_configs = func.__annize__parameter_configs = getattr(func, "__annize__parameter_configs", None) or {}
        param_config = param_configs[arg_name] = (param_configs.get(arg_name)
                                                  or annize.object.controller._CreateObjectHelper.ParameterConfig(arg_name))
        param_config.explicit_only = True
        return func
    return decor
