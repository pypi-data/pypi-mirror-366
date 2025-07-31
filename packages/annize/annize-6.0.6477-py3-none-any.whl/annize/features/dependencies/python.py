# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Python project dependency handling.
"""
import annize.data
import annize.features.dependencies.common
import annize.fs
import annize.i18n


class Python(annize.features.dependencies.common.Dependency):

    def __init__(self, *, version: str, kind, comment):
        super().__init__(kind=kind, label=f"Python {version}", icon="python", comment=comment)


class PythonPackage(annize.features.dependencies.common.Dependency):

    def __init__(self, *, name: str, version: str, kind: annize.features.dependencies.common.Kind|None, comment: annize.i18n.TrStr|None):
        super().__init__(kind=kind, label=f"Python package {name} {version}", icon="python", comment=comment)
        self.__name = name
        self.__version = version

    @property
    def name(self) -> str:
        return self.__name

    @property
    def version(self) -> str:
        return self.__version


class FromRequirementsFile(annize.data.Basket):#TODO ?!?!

    def __init__(self, *, requirements_file: annize.fs.TInputPath = "requirements.txt", kind=None, comment=None):
        dependencies = []
        root_requirements_file = annize.fs.content(requirements_file).path()
        requirements_files = [root_requirements_file]
        while requirements_files:
            requirements_file = requirements_files.pop(0)
            for requirement_line in requirements_file.read_text().split("\n"):
                requirement_line = requirement_line.strip()
                if not requirement_line or requirement_line.startswith("#"):
                    continue
                if requirement_line.startswith("-r"):
                    requirements_files.append(root_requirements_file.parent(requirement_line[3:].strip()))
                    continue
                package_name, _, package_version = requirement_line.partition(" ")
                dependencies.append(PythonPackage(name=package_name.strip(), version=package_version.strip(), kind=kind,
                                                  comment=comment))
        super().__init__(dependencies)
