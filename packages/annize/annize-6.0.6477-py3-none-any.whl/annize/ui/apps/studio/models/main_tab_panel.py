# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.ui.apps.studio.models.problems_list
import annize.ui.apps.studio.models.project_config


class MainTabPanel(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    problems_list: "annize.ui.apps.studio.models.problems_list.ProblemsList|None" = klovve.model.property()

    def _(self):
        if not self.problems_list:
            return ""
        problem_count = len(self.problems_list.problems2)
        return annize.i18n.tr("an_UI_problems").format(
            n=problem_count if problem_count else annize.i18n.tr("an_UI_problemsNone"))
    problems_tab_title: str = klovve.model.computed_property(_)

    project_configs: list[annize.ui.apps.studio.models.project_config.ProjectConfig] = klovve.ui.list_property()

    _jump_to_node: klovve.ui.View|None = klovve.model.property()

    def jump_to_node(self, node: "annize.project.Node") -> None:
        #TODO xx dirty
        self._jump_to_node = node
        self._jump_to_node = None
