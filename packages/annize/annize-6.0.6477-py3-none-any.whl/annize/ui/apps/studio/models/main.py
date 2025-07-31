# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve

import annize.flow.run_context
import annize.i18n
import annize.project.loader
import annize.project.materializer
import annize.ui.apps.studio.models.main_tab_panel
import annize.ui.apps.studio.models.object_editor
import annize.ui.apps.studio.models.problems_list
import annize.ui.apps.studio.models.project_config


class Main(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    project: "annize.project.Project|None" = klovve.ui.property()

    main_tab_panel: "annize.ui.apps.studio.models.main_tab_panel.MainTabPanel|None" = klovve.ui.property()

    problems_list: "annize.ui.apps.studio.models.problems_list.ProblemsList|None" = klovve.model.property()

    project_configs: list[annize.ui.apps.studio.models.project_config.ProjectConfig] = klovve.ui.list_property()

    problems_by_node: dict["annize.project.Node", list["annize.ui.apps.studio.models.problems_list.Problem"]] = klovve.ui.property(initial=lambda: {})

    def _(self):#TODO xx
        if self.project:
            self.saved_snapshot = 0
            self.undone_snapshots = ()
            self.undoable_snapshots = (0,)
            self.project_configs = (annize.ui.apps.studio.models.project_config.ProjectConfig(
                annize_application=self.bind.annize_application,
                label=annize.i18n.tr("an_UI_allObjects"),
                object_editor=annize.ui.apps.studio.models.object_editor.ObjectEditor(
                    annize_application=self.bind.annize_application,
                    project=self.project,
                    node=self.project.node,
                    problems_by_node=self.bind.problems_by_node,
                    is_expanded=True
                ),
                is_closable=False),)
            self.problems_list = annize.ui.apps.studio.models.problems_list.ProblemsList(
                annize_application=self.bind.annize_application,
                problems=self.bind.problems_by_node
            )
            self.main_tab_panel = annize.ui.apps.studio.models.main_tab_panel.MainTabPanel(
                annize_application=self.bind.annize_application,
                problems_list=self.bind.problems_list,
                project_configs=self.bind.project_configs
            )
            self.__determine_problems()
    foocy = klovve.model.computed_property(_)

    saved_snapshot: int = klovve.model.property(initial=0)

    undoable_snapshots: list = klovve.model.list_property()

    undone_snapshots: list = klovve.model.list_property()

    def _(self) -> bool:
        if len(self.undoable_snapshots) == 0:
            return False
        return self.__cleaned_snapshot_list(self.undoable_snapshots)[-1] != self.saved_snapshot
    has_unsaved_changes: bool = klovve.model.computed_property(_)

    def _(self) -> bool:
        return self.project is not None
    can_run: bool = klovve.model.computed_property(_)

    def _(self) -> bool:
        return len(self.__cleaned_snapshot_list(self.undoable_snapshots)) > 1
    can_undo_change: bool = klovve.model.computed_property(_)

    def _(self) -> bool:
        return len(self.undone_snapshots) > 0
    can_redo_change: bool = klovve.model.computed_property(_)

    def save_changes(self):
        self.project.save()
        self.saved_snapshot = self.__cleaned_snapshot_list(self.undoable_snapshots)[-1]

    def undo_change(self):
        if not self.can_undo_change:
            return
        cleanedsnapshots = self.__cleaned_snapshot_list(self.undoable_snapshots)
        self.undone_snapshots.append(cleanedsnapshots[-1])
        self.project.node.undo_changes(cleanedsnapshots[-2])
        self.__snapshot()
        self.prn()

    def redo_change(self):
        if not self.can_redo_change:
            return
        undone_remaining, undone_last = self.undone_snapshots[:-1], self.undone_snapshots[-1]
        self.project.node.undo_changes(undone_last)
        self.__snapshot()
        self.undone_snapshots = undone_remaining
        self.prn()

    def create_or_load_project(self, project_dir):
        if self.is_valid_project_dir(project_dir):
            self.project = annize.project.Project.load(project_dir)
        else:
            self.project = annize.project.Project.create_new(project_dir)

    def is_valid_project_dir(self, project_dir):
        return bool(annize.project.loader.find_project_annize_config_root_file(project_dir))

    def __snapshot(self):
        next_history_index = self.undoable_snapshots[-1]
        changes = self.project.node.get_changes(since=next_history_index)
        next_history_index += len(changes)
        self.undoable_snapshots.append(next_history_index)

    def snapshot(self):
        self.__snapshot()
        self.undone_snapshots = ()
        self.__determine_problems()
        self.prn()

    def __cleaned_snapshot_list(self, snapshots: t.Sequence[int]) -> t.Sequence[int]:
        result = []
        if len(snapshots) > 0:
            result.append(snapshots[0])
            lastsnapshot = snapshots[0]
            allevents = self.project.node.get_changes()
            for snapshot in snapshots[1:]:
                if any(allevents[lastsnapshot:snapshot+1]):
                    result.append(snapshot)
                lastsnapshot = snapshot
        return result

    def prn(self):  # TODO weg
        print("\nTODO",
              "\nsnapshots:\n", self.undoable_snapshots,
              "\nevents:\n", self.project.node.get_changes(),
              "\ncleanedsnapshots:\n",self.__cleaned_snapshot_list(self.undoable_snapshots))

    def __determine_problems(self):
        result = {}
        with annize.flow.run_context.RunContext() as context:        # TODO
            context.prepare(annize_config_rootpath=self.project.annize_config_rootpath)
            materialization_result = annize.project.materializer.materialize(self.project.node)  # TODO feature_loader
            for erroneous_node in materialization_result.erroneous_nodes():
                erroneous_node_problems = result[erroneous_node] = []
                for problem in materialization_result.errors_for_node(erroneous_node):
                    erroneous_node_problems.append(annize.ui.apps.studio.models.problems_list.Problem(
                        str(problem), erroneous_node, annize.ui.apps.studio.models.problems_list.Severity.ERROR))
        self.problems_by_node = result
