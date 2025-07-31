# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve.driver

import annize.i18n
import annize.user_feedback


class UserFeedback(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    feedback_tuples: list[tuple[int, klovve.views.interact.AbstractInteract]] = klovve.model.list_property()

    class __(klovve.model.ListTransformer):
        def output_item(self, item):
            return item[1]
    feedback_items: list[klovve.ui.View] = klovve.model.transformed_list_property(__(),
                                                                                  input_list_property=feedback_tuples)

    def _(self):
        return _UserFeedbackController(self)
    feedback_controller: "_UserFeedbackController" = klovve.model.computed_property(_)

    def handle_answered(self, interact: klovve.views.interact.AbstractInteract, answer: object) -> None:
        for i_tuple, (feedback_reqid, feedback_interact) in enumerate(self.feedback_tuples):
            if feedback_interact == interact:
                self.feedback_controller.set_answer(feedback_reqid, answer)
                self.feedback_tuples.pop(i_tuple)
                break


class _UserFeedbackController(annize.user_feedback.UserFeedbackController):

    def __init__(self, user_feedback: UserFeedback):  # TODO scroll-view for message?!
        self.__user_feedback = user_feedback
        self.__nextid = 0
        self.__requests = []  # TODO multithreading  TODO cleanup
        self.__answers = {}  # TODO multithreading  TODO cleanup

    def __get_answer(self, reqid):
        while reqid not in self.__answers:
            pass
        return self.__answers.pop(reqid)

    def set_answer(self, reqid, answer):
        self.__answers[reqid] = answer

    def message_dialog(self, message, answers, config_key):
        reqid, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            feedback_item = klovve.views.interact.Message(
                message=message + _UserFeedbackController.__automate_hint(config_key),
                choices=[(s, i) for i, s in enumerate(answers)])
            self.__user_feedback.feedback_tuples.append((reqid, feedback_item))
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(reqid)

    def input_dialog(self, question, suggested_answer, config_key):
        reqid, self.__nextid = self.__nextid, self.__nextid + 1
        async def _():
            feedback_item = klovve.views.interact.TextInput(
                message=question + _UserFeedbackController.__automate_hint(config_key),
                suggestion=suggested_answer)
            self.__user_feedback.feedback_tuples.append((reqid, feedback_item))
        klovve.driver.Driver.get().loop.enqueue(_())
        return self.__get_answer(reqid)

    def choice_dialog(self, question, choices, config_key):
        pass  # TODO

    @staticmethod
    def __automate_hint(config_key: str|None) -> str:
        if not config_key:
            return ""
        return "\n\n" + annize.i18n.tr("an_UserFeedback_AnswerAutomatableByKey").format(config_key=config_key)
