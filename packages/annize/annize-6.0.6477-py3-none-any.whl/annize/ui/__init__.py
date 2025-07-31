# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import contextlib
import importlib

import klovve


@contextlib.contextmanager
def app(app_name: str, **kwargs):
    application = importlib.import_module(f"annize.ui.apps.{app_name}").Application(**kwargs)

    application_controller = klovve.app.create(application)
    yield application, application_controller
