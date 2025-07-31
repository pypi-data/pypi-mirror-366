#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The Annize CLI.
"""
import argparse
import json
import os
import sys
import typing as t

try:  # weird, but useful in some cases ;)
    if "__main__" == __name__:
        import annize.flow
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.realpath(__file__)+"/../.."))

import annize.asset
import annize.flow.run_context
import annize.i18n
import annize.project.loader
import annize.flow.runner
import annize.ui
import annize.user_feedback.static


def main():
    # TODO
#    import logging
#    logging.basicConfig(level=logging.DEBUG)
    arg_parser = parser(only_documentation=False)
    args = arg_parser.parse_args().__dict__
    command_name = (args.pop("command") or "studio").replace("-", "_")
    command = getattr(Commands(**args), command_name)
    command(**args)


def parser(*, only_documentation: bool = True) -> argparse.ArgumentParser:
    with annize.i18n.annize_user_interaction_culture:
        arg_parser = argparse.ArgumentParser(
            description=None if only_documentation else annize.i18n.tr("an_Cli_welcome").format(
                version=annize.asset.project_info.version,
                readme_file=repr(f"file://{annize.asset.data.readme_pdf(
                    annize.i18n.current_culture().iso_639_1_language_code)}"),
                homepage_url=repr(annize.asset.project_info.homepage_url)))
        arg_parser.add_argument("--project", type=str, help=annize.i18n.tr("an_Cli_project"))
        arg_parser.add_argument("--with-answers-from-json-file", type=str, action="append", default=[],
                                help=annize.i18n.tr("an_Cli_withAnswersFromJsonFile"))
        arg_parser.add_argument("--with-answers-from-json-string", type=str, action="append", default=[],
                                help=annize.i18n.tr("an_Cli_withAnswersFromJsonString"))
        arg_parser.add_argument("--with-answer", type=str, action="append", nargs=2, default=[],
                            help=annize.i18n.tr("an_Cli_withAnswer"))
        p_cmd = arg_parser.add_subparsers(help=annize.i18n.tr("an_Cli_command"), required=False, dest="command",
                                          metavar="[command]")
        p_cmd_do = p_cmd.add_parser("do", help=annize.i18n.tr("an_Cli_do"))
        p_cmd_do.add_argument("task_name", default="", type=str,
                                          help=annize.i18n.tr("an_Cli_task_name"), nargs="?")
        return arg_parser


class Commands:

    __initial_cwd = os.getcwd()

    @classmethod
    def __answers_from_json_files(cls, destination: dict, with_answers_from_json_files: t.Iterable[str]):
        for with_answers_from_json_file in with_answers_from_json_files:
            with open(with_answers_from_json_file, "r") as f:
                json_string = f.read()
            cls.__answers_from_json_strings(destination, [json_string])

    @classmethod
    def __answers_from_json_strings(cls, destination: dict, with_answers_from_json_strings: t.Iterable[str]):
        for with_answers_from_json_string in with_answers_from_json_strings:
            cls.__answers_from_single_answers(destination, json.loads(with_answers_from_json_string).items())

    @classmethod
    def __answers_from_single_answers(cls, destination: dict, with_answers: t.Iterable[t.Tuple[str, str]]):
        for answer_key, answer_value in with_answers:
            destination[answer_key] = answer_value

    def __init__(self, project: str, with_answers_from_json_file: t.Iterable[str],
                 with_answers_from_json_string: t.Iterable[str], with_answer: t.Iterable[t.Tuple[str, str]], **_):
        self.__project = project
        self.__answers = {}
        self.__answers_from_json_files(self.__answers, with_answers_from_json_file)
        self.__answers_from_json_strings(self.__answers, with_answers_from_json_string)
        self.__answers_from_single_answers(self.__answers, with_answer)

    def do(self, task_name: str, **_):
        project = annize.project.Project.load(self.__project or self.__initial_cwd)
        with annize.i18n.annize_user_interaction_culture:  # TODO ?!?! (we already have that somewhere else?! (~10 times!))
            with annize.ui.app("runner", project=project, user_feedback_answers=self.__answers,
                               run_task=task_name) as (app, app_ctrl):
                app_ctrl.run()

    def studio(self, **_):
        project = annize.project.Project.load(self.__project or self.__initial_cwd)
        with annize.i18n.annize_user_interaction_culture:  # TODO ?!?! (we already have that somewhere else?! (~10 times!))
            with annize.ui.app("studio", project=project, user_feedback_answers=self.__answers) as (app, app_ctrl):
                app_ctrl.run()


if __name__ == "__main__":
    main()
