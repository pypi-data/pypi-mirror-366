# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.ui.apps.studio.models.problems_list


class ProblemsList(klovve.ui.ComposedView[annize.ui.apps.studio.models.problems_list.ProblemsList]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.Button(
                    text=annize.i18n.tr("an_UI_jumpToProblem"),
                    horizontal_layout=klovve.ui.Layout(klovve.ui.Align.END),
                    action_name="request_jump_to_selected_problem",
                    style=klovve.views.Button.Style.FLAT,
                    is_enabled=self.model.bind.is_problem_selected),
                klovve.views.List(
                    items=self.model.bind.problems2,
                    item_label_func=self.__problem_to_list_text,
                    selected_item=self.model.bind.selected_problem)])

    def __problem_to_list_text(self, problem: annize.ui.apps.studio.models.problems_list.Problem) -> str:
        severity_str = {
            annize.ui.apps.studio.models.problems_list.Severity.WARNING: "⚠️",
            annize.ui.apps.studio.models.problems_list.Severity.ERROR: "⛔️"}[problem.severity]
        return f"{severity_str} {problem.text}"

    @klovve.event.action("request_jump_to_selected_problem")
    def __handle_request_jump_to_selected_problem(self):
        self.model.handle_request_jump_to_selected_problem()
