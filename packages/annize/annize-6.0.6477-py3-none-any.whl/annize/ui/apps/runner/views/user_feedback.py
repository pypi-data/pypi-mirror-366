# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.ui.apps.runner.models.user_feedback


class UserFeedback(klovve.ui.ComposedView[annize.ui.apps.runner.models.user_feedback.UserFeedback]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=self.model.bind.feedback_items)

    @klovve.event.event_handler
    def __handle_answered(self, event: klovve.views.interact.AbstractInteract.AnsweredEvent):
        self.model.handle_answered(event.interact, event.answer)
        event.stop_processing()
