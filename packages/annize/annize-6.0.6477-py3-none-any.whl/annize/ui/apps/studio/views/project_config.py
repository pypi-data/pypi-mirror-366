# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.ui.apps.studio.models.project_config
import annize.ui.apps.studio.views.object_editor


class ProjectConfig(klovve.ui.ComposedView[annize.ui.apps.studio.models.project_config.ProjectConfig]):

    def compose(self):
        return klovve.views.Placeholder(body=self.bind.object_editor_root)

    def _(self):
        if not self.model:
            return
        return annize.ui.apps.studio.views.object_editor.ObjectEditor(model=self.model.bind.object_editor)
    root_object_editor: annize.ui.apps.studio.views.object_editor.ObjectEditor|None = klovve.ui.computed_property(_)

    def _(self):
        return klovve.views.ObjectEditorRoot(object_editor=self.bind.root_object_editor)
    object_editor_root: klovve.views.ObjectEditorRoot = klovve.ui.computed_property(_)
