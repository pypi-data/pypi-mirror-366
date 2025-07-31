# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.ui.apps.runner.models.task_execution
import annize.ui.apps.runner.views.user_feedback


class TaskExecution(klovve.ui.ComposedView[annize.ui.apps.runner.models.task_execution.TaskExecution]):

    def compose(self):
        if not self.model:
            return

        return klovve.views.VerticalBox(
            items=[
                klovve.views.HeadBar(
                    title=self.model.bind.header_title,
                    style=self.model.bind.header_style),
                annize.ui.apps.runner.views.user_feedback.UserFeedback(
                    model=self.model.bind.user_feedback,
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.START)),
                klovve.views.LogPager(
                    entries=self.model.bind.log_entries)])
