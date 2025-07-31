# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve


class AddChild(klovve.model.Model):

    annize_application: klovve.app.Application = klovve.model.property()

    object_types: list[tuple[str|None, str, type]] = klovve.model.list_property()
