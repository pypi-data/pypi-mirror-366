# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import abc
import sys
import typing as t

import annize.flow.run_context
import annize.data
import annize.i18n


class UserFeedbackController(abc.ABC):

    @abc.abstractmethod
    def message_dialog(self, message: str, answers: list[str], config_key: str|None) -> int:
        pass

    @abc.abstractmethod
    def input_dialog(self, question: str, suggested_answer: str, config_key: str|None) -> str|None:
        pass

    @abc.abstractmethod
    def choice_dialog(self, question: str, choices: list[str], config_key: str|None) -> int|None:
        pass


class NullUserFeedbackController:

    def message_dialog(self, *_):
        raise UnsatisfiableUserFeedbackAttemptError()

    def input_dialog(self, *_):
        raise UnsatisfiableUserFeedbackAttemptError()

    def choice_dialog(self, *_):
        raise UnsatisfiableUserFeedbackAttemptError()


class UnsatisfiableUserFeedbackAttemptError(RuntimeError):

    def __init__(self):
        super().__init__("Attempted to engage in a dialog with the user in a situation that does not allow it.")


_CONTEXT__USERFEEDBACK_CONTROLLERS = annize.data.UniqueId("userfeedback_controllers").processonly_long_str


def _controllers_tuples_for_context(context: annize.flow.run_context.RunContext) -> list[t.Tuple[int, UserFeedbackController]]:
    return context.object_by_name(_CONTEXT__USERFEEDBACK_CONTROLLERS, [(-sys.maxsize, NullUserFeedbackController())],
                                  create_nonexistent=True)


def _controllers_for_context(context: annize.flow.run_context.RunContext) -> list[UserFeedbackController]:
    ctlrtuples = _controllers_tuples_for_context(context)
    ctlrtuples.sort(key=lambda ctlrtuple: -ctlrtuple[0])
    return [ctlrtuple[1] for ctlrtuple in ctlrtuples]


def _add_controller_to_context(*, controller: UserFeedbackController, context: annize.flow.run_context.RunContext,
                               priority_index: int = 0) -> None:
    _controllers_tuples_for_context(context).append((priority_index, controller))


def message_dialog(message: annize.i18n.TrStrOrStr, answers: t.Iterable[annize.i18n.TrStrOrStr], *,
                   config_key: str|None = None) -> int:
    with annize.i18n.annize_user_interaction_culture:  #TODO also in the other functions
        for controller in _controllers_for_context(annize.flow.run_context.current()):
            try:
                return controller.message_dialog(str(message), [str(ans) for ans in answers], config_key)
            except UnsatisfiableUserFeedbackAttemptError:
                pass
        raise UnsatisfiableUserFeedbackAttemptError()


def input_dialog(message: annize.i18n.TrStrOrStr, *, suggested_answer: annize.i18n.TrStrOrStr,
                 config_key: str|None = None) -> str|None:
    for controller in _controllers_for_context(annize.flow.run_context.current()):
        try:
            return controller.input_dialog(str(message), str(suggested_answer), config_key)
        except UnsatisfiableUserFeedbackAttemptError:
            pass
    raise UnsatisfiableUserFeedbackAttemptError()


def choice_dialog(message: annize.i18n.TrStrOrStr, choices: t.Iterable[annize.i18n.TrStrOrStr], *,
                  config_key: str|None = None) -> int|None:
    for controller in _controllers_for_context(annize.flow.run_context.current()):
        try:
            return controller.choice_dialog(str(message), [str(choice) for choice in choices], config_key)
        except UnsatisfiableUserFeedbackAttemptError:
            pass
    raise UnsatisfiableUserFeedbackAttemptError()
