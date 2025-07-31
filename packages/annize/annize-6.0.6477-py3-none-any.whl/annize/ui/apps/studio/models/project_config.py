# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.ui.apps.studio.models.object_editor


class ProjectConfig(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    label: str = klovve.model.property(initial="")

    is_closable: bool = klovve.model.property(initial=True)

    object_editor: "annize.ui.apps.studio.models.object_editor.ObjectEditor|None" = klovve.model.property()

    def _(self):
        MAX_LEN = 40
        if len(self.label) <= MAX_LEN:
            return self.label
        return f"{self.label[:MAX_LEN//2] + "…" + self.label[-MAX_LEN//2:]}"
    shortened_label: str = klovve.model.computed_property(_)
