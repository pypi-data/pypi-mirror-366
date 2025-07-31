# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Python Wheels.
"""
import dataclasses
import os
import subprocess
import typing as t

import annize.data
import annize.features.authors
import annize.features.base
import annize.features.dependencies.python
import annize.features.licensing
import annize.fs
import annize.i18n


if False:
    annize.i18n.tr("an_int_PythonWheelPackage")  # to be used by Annize projects


class ExecutableLink:

    def __init__(self, *, link_name: str, module_name: str, method_name: str, is_gui: bool):
        self.__linkname = link_name
        self.__modulename = module_name
        self.__methodname = method_name
        self.__is_gui = is_gui

    @property
    def link_name(self) -> str:
        return self.__linkname

    @property
    def module_name(self) -> str:
        return self.__modulename

    @property
    def method_name(self) -> str:
        return self.__methodname

    @property
    def is_gui(self) -> bool:
        return self.__is_gui


class ExtraDependencies:

    def __init__(self, *, extra_name: str, dependencies: t.Iterable[annize.features.dependencies.python.PythonPackage]):
        self.__extra_name = extra_name
        self.__dependencies = tuple(dependencies)

    @property
    def extra_name(self) -> str:
        return self.__extra_name

    @property
    def dependencies(self) -> t.Sequence[annize.features.dependencies.python.PythonPackage]:
        return self.__dependencies


class Package(annize.fs.FilesystemContent):

    def __init__(self, *, source: annize.fs.FilesystemContent, executable_links: t.Iterable[ExecutableLink],
                 packagename: str|None, description: annize.i18n.TrStr|None,
                 homepage_url: str|None, long_description: annize.i18n.TrStr|None,
                 version: annize.data.Version|None, keywords: annize.features.base.Keywords|None,
                 dependencies: t.Iterable[annize.features.dependencies.python.PythonPackage],
                 extra_dependencies: t.Iterable[ExtraDependencies],
                 license: annize.features.licensing.License|None,
                 authors: t.Iterable[annize.features.authors.Author],):
        super().__init__(self._path)
        self.__source = source
        self.__executable_links = tuple(executable_links)
        self.__packagename = packagename
        self.__description = description
        self.__homepage_url = homepage_url
        self.__long_description = long_description
        self.__version = version
        self.__keywords = keywords
        self.__dependencies = dependencies
        self.__extra_dependencies = extra_dependencies
        self.__license = license
        self.__authors = tuple(authors)

    def _path(self):
        with annize.i18n.culture_by_spec("en"):  # TODO zz
            license = self.__license
            if not license:
                projlics = annize.features.licensing.project_licenses()
                if len(projlics) > 0:
                    license = projlics[0]  # TODO only 1st?!
                else:
                    license = object()#TODO
            return self._mkpackage(self._BuildInfo(
                source=self.__source,
                long_description=self.__long_description or annize.features.base.long_description(),
                homepage=self.__homepage_url or annize.features.base.homepage_url(),
                description=self.__description or annize.features.base.summary(),
                keywords=self.__keywords or annize.features.base.project_keywords(),
                name=self.__packagename or annize.features.base.project_name(),
                author=annize.features.authors.join_authors(self.__authors or annize.features.authors.project_authors()),
                license=license,
                dependencies=self.__dependencies,
                extra_dependencies=self.__extra_dependencies,
                executable_links=self.__executable_links,
                version=self.__version)).path()

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        description: str
        long_description: str
        keywords: annize.features.base.Keywords
        name: str
        version: annize.data.Version
        homepage: str
        author: annize.features.authors.Author
        license: annize.features.licensing.License
        executable_links: list[ExecutableLink]
        dependencies: list
        extra_dependencies: list
        pkgrootpath: str = None
        pkgpath_setuppy: str = None
        setuppy_conf: dict[str, t.Any|None] = None
        result: annize.fs.FilesystemContent = None

    @classmethod
    def _mkpackage(cls, build: _BuildInfo) -> annize.fs.FilesystemContent:
        with annize.fs.fresh_temp_directory() as tmpdir:
            # TODO review impl
            """
            TODO
            for src, dst in [("README", f"/usr/share/doc/{universe.name}/README"),
                             ("README.pdf", f"/usr/share/doc/{universe.name}/README.pdf")]:
            """        """#TODO
            if .utils.basic.call("fakeroot -v", shell=True)[0] != 0:
                raise .framework.exceptions.RequirementsMissingError("'fakeroot' seems to be unavailable")
            if .utils.basic.call("dpkg --version", shell=True)[0] != 0:
                raise .framework.exceptions.RequirementsMissingError("'dpkg' seems to be unavailable")
            """
            cls._mkpackage_prepareinfos(build, tmpdir)
            cls._mkpackage_setuppyconf_prepare(build)
            cls._mkpackage_setuppyconf_install_requires(build)
            cls._mkpackage_setuppyconf_classifiers(build)
            cls._mkpackage_mkexeclinks(build)
            cls._mkpackage_mksetuppyconf(build)
            cls._mkpackage_mkmanifestin(build)
            cls._mkpackage_bdist_wheel(build)
            return build.result.path().temp_clone()

    @classmethod
    def _mkpackage_prepareinfos(cls, build: _BuildInfo, tmpdir: annize.fs.Path) -> None:
        build.pkgrootpath = f"{tmpdir}/wheelpkg"
        build.source.path().copy_to(build.pkgrootpath)
        build.setuppy_conf = {}
        build.pkgpath_setuppy = f"{build.pkgrootpath}/setup.py"
        if os.path.exists(build.pkgpath_setuppy):
            raise Exception("TODO There must be no setup.py in the project root.")

    @classmethod
    def _mkpackage_setuppyconf_prepare(cls, build: _BuildInfo) -> None:
        build.setuppy_conf["name"] = build.name
        build.setuppy_conf["version"] = str(build.version)
        build.setuppy_conf["description"] = str(build.description)
        build.setuppy_conf["long_description"] = str(build.long_description)
        build.setuppy_conf["description_content_type"] = "text/plain"
        build.setuppy_conf["long_description_content_type"] = "text/plain"
        build.setuppy_conf["url"] = str(build.homepage)
        build.setuppy_conf["author"] = str(build.author.full_name)
        build.setuppy_conf["author_email"] = str(build.author.email)
        build.setuppy_conf["license"] = str(build.license.name)
        build.setuppy_conf["include_package_data"] = True
        if build.keywords.keywords:
            build.setuppy_conf["keywords"] = " ".join([str(kwd) for kwd in build.keywords.keywords])

    @classmethod
    def _mkpackage_setuppyconf_install_requires(cls, build: _BuildInfo) -> None:
        build.setuppy_conf["install_requires"] = [f"{dependency.name} {dependency.version}" for dependency in build.dependencies]
        build.setuppy_conf["extras_require"] = {extra_dependencies.extra_name: [f"{dependency.name} {dependency.version}" for dependency in extra_dependencies.dependencies] for extra_dependencies in build.extra_dependencies}

    @classmethod
    def _mkpackage_setuppyconf_classifiers(cls, build: _BuildInfo) -> None:
        build.setuppy_conf["classifiers"] = [] # TODO
        #TODO license classifier

    @classmethod
    def _mkpackage_mkexeclinks(cls, build: _BuildInfo) -> None:
        console_scripts = []
        gui_scripts = []
        for executable_link in build.executable_links:
            lst = gui_scripts if executable_link.is_gui else console_scripts
            lst.append(f"{executable_link.link_name}={executable_link.module_name}:{executable_link.method_name}")
        build.setuppy_conf["entry_points"] = {
            "console_scripts": console_scripts,
            "gui_scripts": gui_scripts
        }

    @classmethod
    def _mkpackage_mksetuppyconf(cls, build: _BuildInfo) -> None:
        setuppyconfcode = ""
        for confkey, value in build.setuppy_conf.items():
            setuppyconfcode += f"{confkey}={repr(value)},"
        with open(build.pkgpath_setuppy, "w") as f:
            f.write(f"import setuptools\n"
                    f"setuptools.setup(\n"
                    f"    {setuppyconfcode}\n"
                    f"    packages=setuptools.find_packages()+setuptools.find_namespace_packages()\n"
                    f")\n")

    @classmethod
    def _mkpackage_bdist_wheel(cls, build: _BuildInfo) -> None:
        subprocess.check_call(["python3", "setup.py", "bdist_wheel", "--python-tag", "py3"], cwd=build.pkgrootpath)
        distfs = annize.fs.Path(build.pkgrootpath)("dist")
        build.result = distfs.children()[0]

    @classmethod
    def _mkpackage_mkmanifestin(cls, build: _BuildInfo) -> None:
        with open(f"{build.pkgrootpath}/MANIFEST.in", "w") as f:
            f.write("graft **\n"
                    "global-exclude *.py[cod]\n")


"""TODO
try:
    import setuptools as _foo_test_setuptools
except ImportError as exc:
    raise .framework.exceptions.RequirementsMissingError("'setuptools' seem to be unavailable", exc)
if .utils.basic.call("wheel version", shell=True)[0] != 0:
    raise .framework.exceptions.RequirementsMissingError("'wheel' seems to be unavailable")
    """
