# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Flatpaks.
"""
import dataclasses
import os
import subprocess
import typing as t

import annize.features.base
import annize.features.distributables.common
import annize.fs
import annize.i18n


if False:
    annize.i18n.tr("an_int_FlatpakPackage")  # to be used by Annize projects


class MenuEntry:

    def __init__(self, *, name: str, title: annize.i18n.TrStr, category: t.Tuple, command: str, is_gui: bool,
                 icon: annize.fs.FilesystemContent|None):
        self.__name = name
        self.__title = title
        self.__category = category
        self.__command = command
        self.__is_gui = is_gui
        self.__icon = icon

    @property
    def name(self) -> str:
        return self.__name

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    @property
    def category(self) -> t.Tuple:  #TODO
        return self.__category

    @property
    def command(self) -> str:
        return self.__command

    @property
    def is_gui(self) -> bool:
        return self.__is_gui

    @property
    def icon(self) -> annize.fs.FilesystemContent|None:
        return self.__icon


class Filesystem:

    def __init__(self, **b):
        pass  # TODO


class Share:

    def __init__(self, **b):
        pass  # TODO


class EnvironmentVariable:

    def __init__(self, **b):
        pass  # TODO


class Repository:

    def __init__(self, *, public_url: str, friendly_name_suggestion: str|None):
        self.__public_url = public_url
        self.__friendly_name_suggestion = friendly_name_suggestion

    def upload(self, source: annize.fs.FilesystemContent):
        pass  # TODO implement or abstract?!

    @property
    def public_url(self) -> str:
        return self.__public_url

    @property
    def friendly_name_suggestion(self) -> str:
        return self.__friendly_name_suggestion or os.path.basename(self.public_url)


class LocalRepository(Repository):
    #TODO refactor to sth like "FsEntryRepository" (or put it just to repository)

    def __init__(self, *, public_url: str, friendly_name_suggestion: str|None, upload_path: str|None,
                 upload_fsentry: annize.fs.FilesystemContent|None):
        super().__init__(public_url=public_url, friendly_name_suggestion=friendly_name_suggestion)
        self.__public_url = public_url
        self.__friendly_name_suggestion = friendly_name_suggestion
        self.__upload_path = upload_path or upload_fsentry.path()

    def upload(self, source: annize.fs.FilesystemContent):
        source.path().copy_to(self.__upload_path, overwrite=True)


class Group(annize.features.distributables.common.Group):

    def __init__(self, *, source: annize.fs.FilesystemContent, title: str, description: annize.i18n.TrStr|None,
                 repository: Repository, package_name: str, project_short_hint_name: str|None,
                 package_short_name: str|None):
        flatpakreffile = FlatpakrefFile(refname=package_short_name, package_name=package_name,
                                        title=project_short_hint_name, repository=repository,
                                        runtime_repository_url=None, gpgkey=b"TODO")  # TODO runtime_repository_url?!
        gpgfile = GpgFile(refname=package_short_name, gpgkey=b"TODO abc")
        super().__init__(title=title, description=description, files=[flatpakreffile, gpgfile], package_store=None)
        self.__repository = repository
        self.__source = source
        self.__package_name = package_name
        self.__project_short_hint_name = project_short_hint_name
        self.__package_short_name = package_short_name
        self.__flatpak_built = False

    def files(self):
        if not self.__flatpak_built:
            self.__repository.upload(FlatpakImage(source=self.__source, package_name=self.__package_name))
            self.__flatpak_built = True
        return super().files()

    @property
    def description(self):
        distrihowtos = ""
        project_short_hint_name = self.__project_short_hint_name or annize.features.base.pretty_project_name()
        repository_friendly_name = self.__repository.friendly_name_suggestion
        repository_public_url = self.__repository.public_url
        package_name = self.__package_name
        for distriname, distrihowto in {  # TODO howto list still up to date?
            "archlinux": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_archlinux"),
            "centos": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_centos"),
            "debian": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_debian"),
            "fedora": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_fedora"),
            "gentoo": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_gentoo"),
            "opensuse": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_opensuse"),
            "redhat": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_redhat"),
            "ubuntu": annize.i18n.TrStr.tr("an_Dist_FlatpakDesc_distrihowto_ubuntu")
        }.items():
            distrihowtos += (f".. container:: annizedoc-infobutton\n\n"
                             f"  |annizeicon_{distriname}|\n\n"
                             f"  .. hint:: \n    {distrihowto}\n\n")
        intro = annize.i18n.TrStr.tr("an_Dist_FlatpakDesc").format(**locals())
        outrotxt = annize.i18n.TrStr.tr("an_Dist_FlatpakDescOutro")
        outroposttxt = annize.i18n.TrStr.tr("an_Dist_FlatpakDescOutroPost")
        outro = annize.i18n.to_trstr(
            ".. rst-class:: annizedoc-infobutton-stop\n\n"
            "{outrotxt}\n\n"
            ".. code-block:: sh\n\n"
            "  $ flatpak remote-add --user --no-gpg-verify {repository_friendly_name} {repository_public_url}\n"
            "  $ flatpak install --user {repository_friendly_name} {package_name}\n"
            "  $ flatpak run {package_name}\n\n"
            "{outroposttxt}").format(**locals())
        return annize.i18n.to_trstr("{intro}\n\n{distrihowtos}\n\n{outro}").format(**locals())


"""TODO zz (maybe this should be even mentioned first?!)
or install it with just:

$ flatpak install --user --from https://pseudopolis.eu/wiki/pino/projs/foo/foo.flatpakref
"""


class FlatpakrefFile(annize.fs.FilesystemContent):

    def __init__(self, *, refname: str|None, package_name: str, title: str|None, branch: str = "master",
                 runtime_repository_url: str|None, gpgkey: bytes|None, repository: Repository):
        super().__init__(self._path)
        self.__refname = refname
        self.__package_name = package_name
        self.__title = title
        self.__branch = branch
        self.__runtime_repository_url = runtime_repository_url
        self.__gpgkey = gpgkey
        self.__repository = repository

    def _path(self):
        refname = self.__refname or annize.features.base.project_name()
        title = self.__title or refname
        res = {"Title": title, "Name": self.__package_name, "Branch": self.__branch,
               "Url": self.__repository.public_url, "IsRuntime": "False"}
        if self.__gpgkey:
            res["GPGKey"] = self.__gpgkey.decode()
        if self.__runtime_repository_url:  # TODO
            res["RuntimeRepo"] = self.__runtime_repository_url
        flatpakrefcont = "\n".join([f"{x}={res[x]}" for x in res])
        return annize.fs.dynamic_file(content=f"[Flatpak Ref]\n{flatpakrefcont}\n",
                                           file_name=f"{refname}.flatpakref").path()


class GpgFile(annize.fs.FilesystemContent):

    def _path(self):
        refname = self.__refname or annize.features.base.project_name()
        return annize.fs.dynamic_file(content="TODO zz fritten.gpg",
                                                file_name=f"{refname}.gpg").path()

    def __init__(self, *, refname: str = None, gpgkey: bytes = None):
        super().__init__(self._path)
        self.__refname = refname
        self.__gpgkey = gpgkey


class FlatpakImage(annize.fs.FilesystemContent):

    def __init__(self, *, source: annize.fs.FilesystemContent, package_name: str, sockets: t.Iterable[str] = ("x11",),
                 filesystems: t.Iterable[str] = ("home",), shares: t.Iterable[str] = ("network",)):
        super().__init__(self._path)
        self.__source = source
        self.__package_name = package_name
        self.__sockets = sockets
        self.__filesystems = filesystems
        self.__shares = shares

    def _path(self):
        return self._mkpackage(self._BuildInfo(source=self.__source,  name=self.__package_name, sdk="org.freedesktop.Sdk", platform="org.freedesktop.Platform", kitversion="19.08",
                                               command=None,
                                               sockets=self.__sockets,
                                               filesystems=self.__filesystems,
                                               shares=self.__shares,
                                               menu_entries=[],
                                               environment={}))

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        name: str
        sdk: str
        platform: str
        kitversion: str|None
        command: str|None #TODO
        sockets: t.Iterable[str]
        filesystems: t.Iterable[str]
        shares: t.Iterable[str]
        menu_entries: t.Iterable[MenuEntry]
        environment: dict[str, str]  # TODO
        pkgrootpath: str = None
        pkgpath_share: str = None
        pkgpath_share_applications: str = None
        pkgpath_share_icons: str = None
        result: annize.fs.FilesystemContent = None

    @classmethod
    def _mkpackage_prepareinfos(cls, build: _BuildInfo, tmpdir: annize.fs.Path) -> None:
        build.pkgrootpath = f"{tmpdir}/pkg"
        build.pkgpath_share = f"{build.pkgrootpath}/export/share"
        build.pkgpath_share_applications = f"{build.pkgpath_share}/applications"
        build.pkgpath_share_icons = f"{build.pkgpath_share}/icons"
        for pkgpath in [build.pkgpath_share_applications, build.pkgpath_share_icons]:
            os.makedirs(f"{build.pkgrootpath}/{pkgpath}", exist_ok=True)

    @classmethod
    def _mkpackage_flatpak_build_init(cls, build: _BuildInfo) -> None:
        kitversionopts = [build.kitversion] if build.kitversion else []
        subprocess.check_call(["flatpak", "build-init", build.pkgrootpath, build.name, build.sdk, build.platform,
                               *kitversionopts])

    @classmethod
    def _mkpackage_applysource(cls, build: _BuildInfo) -> None:
        build.source.path().copy_to(build.pkgrootpath, destination_as_parent=True, merge=True)

    @classmethod
    def _mkpackage_flatpak_build_finish(cls, build: _BuildInfo) -> None:
        opts = []
        if build.command:
            opts.append(f"--command={build.command}")
        for s in build.sockets:
            opts.append(f"--socket={s}")
        for s in build.filesystems:
            opts.append(f"--filesystem={s}")
        for s in build.shares:
            opts.append(f"--share={s}")
        for envk, envv in build.environment.items():
            opts.append(f"--env={envk}={envv}")
        subprocess.check_call(["flatpak", "build-finish", build.pkgrootpath])

    @classmethod
    def _mkpackage_share(cls, build: _BuildInfo) -> None:
        for menuentry in build.menu_entries:
            iconfname = f"{build.name}.{menuentry.name}.png"
            icondst = annize.fs.Path(build.pkgpath_share_icons)(iconfname)
            entryaux = ""
            if menuentry.icon:
                menuentry.icon.copy_to(icondst)
                entryaux += f"Icon={iconfname}\n"
            with open(f"{build.pkgpath_share_applications}/{build.name}.{menuentry.name}.desktop", "w") as f:
                f.write(f"[Desktop Entry]\n"
                        f"Name={menuentry.title}\n"
                        f"Exec={menuentry.command}\n"
                        f"Terminal={'false' if menuentry.is_gui else 'true'}\n"
                        f"Type=Application\n"
                        f"Categories={menuentry.category[1]};\n"
                        f"{entryaux}")

    @classmethod
    def _mkpackage_flatpak_build_export(cls, build: _BuildInfo) -> None:
        build.result = annize.fs.fresh_temp_directory().path
        respath = build.result.path()
        opts = [] # TODO zz gpg stoff
        subprocess.check_call(["flatpak", "build-export", *opts, respath, build.pkgrootpath])
        subprocess.check_call(["flatpak", "build-update-repo", *opts, respath])

    @classmethod
    def _mkpackage(cls, build: _BuildInfo) -> annize.fs.Path:
        with annize.fs.fresh_temp_directory() as tmpdir:
            cls._mkpackage_prepareinfos(build, tmpdir)
            cls._mkpackage_flatpak_build_init(build)
            cls._mkpackage_applysource(build)
            cls._mkpackage_flatpak_build_finish(build)
            cls._mkpackage_flatpak_build_export(build)
            return build.result.path()
