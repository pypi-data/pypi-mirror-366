# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import dataclasses
import enum

import klovve

import annize.project


class Severity(enum.Enum):
    WARNING = enum.auto()
    ERROR = enum.auto()


@dataclasses.dataclass(frozen=True)
class Problem:
    text: str
    node: "annize.project.Node"
    severity: Severity


class ProblemsList(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    problems: dict["annize.project.Node", list[Problem]] = klovve.model.property(initial=lambda: {})

    selected_problem: Problem|None = klovve.model.property()

    def _(self):
        result = []
        for node, problems in self.problems.items():
            for problem in problems:
                result.append(problem)
        return result
    problems2 = klovve.model.computed_list_property(_)

    def _(self):
        return self.selected_problem is not None
    is_problem_selected = klovve.model.computed_property(_)

    def handle_request_jump_to_selected_problem(self):
        if self.selected_problem:
            self.annize_application.jump_to_node(self.selected_problem.node)
