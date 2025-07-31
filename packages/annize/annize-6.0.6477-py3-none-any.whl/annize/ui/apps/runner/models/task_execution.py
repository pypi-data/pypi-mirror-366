# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.flow.runner
import annize.ui.apps.runner.models.user_feedback


class TaskExecution(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    runner: annize.flow.runner.Runner|None = klovve.model.property()

    user_feedback: "annize.ui.apps.runner.models.user_feedback.UserFeedback|None" = klovve.model.property()

    project_name: str = klovve.model.property(initial="")

    task_name: str = klovve.model.property(initial="")

    status_text: str = klovve.model.property(initial="")

    header_style: klovve.views.HeadBar.Style = klovve.model.property(initial=klovve.views.HeadBar.Style.BUSY)

    log_entries: list[klovve.views.LogPager.Entry] = klovve.model.list_property()

    def _(self):
        return f"{self.project_name}\n{self.task_name}\n{self.status_text}"
    header_title: str = klovve.model.computed_property(_)
