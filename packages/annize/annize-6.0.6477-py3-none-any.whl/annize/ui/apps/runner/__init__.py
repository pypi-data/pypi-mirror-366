# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve
import typing as t

import annize.project.loader


class Application(klovve.app.Application):

    project: "annize.project.Project" = klovve.ui.property()

    user_feedback_answers: dict[str, t.Any] = klovve.ui.property(initial=lambda: {})

    run_task: str|None = klovve.ui.property()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from annize.ui.apps.runner.models.main import Main as MainModel
        from annize.ui.apps.runner.views.main import Main as MainView

        self.windows.append(klovve.views.Window(
            title="Annize",
            body=MainView(
                model=MainModel(
                    annize_application=self,
                    project=self.bind.project,
                    run_task=self.bind.run_task))))
