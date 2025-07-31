# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import hallyd


data_dir = hallyd.fs.Path(__file__).parent("_static")

mo_dir = data_dir("mo")

icons_dir = data_dir("icons")

licenses_dir = data_dir("licenses")

annize_png = data_dir("annize.png")


def readme_pdf(culture: str) -> hallyd.fs.Path:
    for culture in (culture, "en"):
        if (readme_pdf := data_dir(f"README/{culture}.pdf")).exists():
            return readme_pdf
