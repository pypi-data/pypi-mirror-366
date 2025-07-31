# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
#TODO weg?!
import typing as t

import annize.user_feedback


class StaticUserFeedbackController(annize.user_feedback.UserFeedbackController):

    def __init__(self, answers: dict[str, t.Any]):
        self.__answers = dict(answers)

    def add_answer(self, config_key: str, value: t.Any) -> None:
        self.__answers[config_key] = value

    def __get_answer(self, config_key: str) -> t.Any:
        if config_key:
            answer = self.__answers.get(config_key, self)
            if answer is not self:
                return answer
        raise annize.user_feedback.UnsatisfiableUserFeedbackAttemptError()

    def message_dialog(self, message, answers, config_key):
        answer = int(self.__get_answer(config_key))
        if not (0 <= answer < len(answers)):
            raise Exception("TODO out of range")  # TODO check in superclass
        return answer

    def input_dialog(self, question, suggested_answer, config_key):
        answer = self.__get_answer(config_key)
        if answer == "---":
            return None
        if answer == "!!!":
            return suggested_answer
        return answer

    def choice_dialog(self, question, choices, config_key):
        answer = int(self.__get_answer(config_key))
        if answer == -1:
            return None
        if not (0 <= answer < len(choices)):
            raise Exception("TODO out of range")  # TODO check in superclass
        return answer
