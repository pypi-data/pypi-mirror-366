# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Debian (.deb) packages.
"""
import dataclasses
import datetime
import gzip
import math
import os
import subprocess
import typing as t

import annize.object
import annize.data
import annize.features.authors
import annize.features.base
import annize.features.dependencies.common
import annize.features.distributables.common
import annize.fs
import annize.i18n


if False:
    annize.i18n.tr("an_int_DebianPackage")  # to be used by Annize projects


class Category:

    def __init__(self, *, debian_name: str, freedesktop_name: str):
        self.__debian_name = debian_name
        self.__freedesktop_name = freedesktop_name

    @property
    def debian_name(self) -> str:
        return self.__debian_name

    @property
    def freedesktop_name(self) -> str:
        return self.__freedesktop_name


class MenuEntry:

    @annize.object.explicit_only("icon")
    def __init__(self, *, name: str, title: annize.i18n.TrStr, category: Category, command: str, is_gui: bool,
                 icon: annize.fs.TFilesystemContent|None):
        self.__name = name
        self.__title = title
        self.__category = category
        self.__command = command
        self.__is_gui = is_gui
        self.__icon = None if icon is None else annize.fs.content(icon)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title

    @property
    def category(self) -> Category|None:
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


class ExecutableLink:

    def __init__(self, *, path: str, name: str|None):
        self.__path = path
        self.__name = name or os.path.splitext(os.path.basename(path))[1]

    @property
    def path(self) -> str:
        return self.__path

    @property
    def name(self) -> str:
        return self.__name


def _debian_category(debian_name: str, freedesktop_name: str) -> type[Category]:
    class ACategory(Category):
        def __init__(self):
            super().__init__(debian_name=debian_name, freedesktop_name=freedesktop_name)
    return ACategory


ApplicationsAccessibilityCategory = _debian_category("Applications/Accessibility", "System")
ApplicationsAmateurradioCategory = _debian_category("Applications/Amateur Radio", "Utility")
ApplicationsDatamanagementCategory = _debian_category("Applications/Data Management", "System")
ApplicationsEditorsCategory = _debian_category("Applications/Editors", "Utility")
ApplicationsEducationCategory = _debian_category("Applications/Education", "Education")
ApplicationsEmulatorsCategory = _debian_category("Applications/Emulators", "System")
ApplicationsFilemanagementCategory = _debian_category("Applications/File Management", "System")
ApplicationsGraphicsCategory = _debian_category("Applications/Graphics", "Graphics")
ApplicationsMobiledevicesCategory = _debian_category("Applications/Mobile Devices", "Utility")
ApplicationsNetworkCategory = _debian_category("Applications/Network", "Network")
ApplicationsNetworkCommunicationCategory = _debian_category("Applications/Network/Communication", "Network")
ApplicationsNetworkFiletransferCategory = _debian_category("Applications/Network/File Transfer", "Network")
ApplicationsNetworkMonitoringCategory = _debian_category("Applications/Network/Monitoring", "Network")
ApplicationsNetworkWebbrowsingCategory = _debian_category("Applications/Network/Web Browsing", "Network")
ApplicationsNetworkWebnewsCategory = _debian_category("Applications/Network/Web News", "Network")
ApplicationsOfficeCategory = _debian_category("Applications/Office", "Office")
ApplicationsProgrammingCategory = _debian_category("Applications/Programming", "Development")
ApplicationsProjectmanagementCategory = _debian_category("Applications/Project Management", "Development")
ApplicationsScienceCategory = _debian_category("Applications/Science", "Education")
ApplicationsScienceAstronomyCategory = _debian_category("Applications/Science/Astronomy", "Education")
ApplicationsScienceBiologyCategory = _debian_category("Applications/Science/Biology", "Education")
ApplicationsScienceChemistryCategory = _debian_category("Applications/Science/Chemistry", "Education")
ApplicationsScienceDataanalysisCategory = _debian_category("Applications/Science/Data Analysis", "Education")
ApplicationsScienceElectronicsCategory = _debian_category("Applications/Science/Electronics", "Education")
ApplicationsScienceEngineeringCategory = _debian_category("Applications/Science/Engineering", "Education")
ApplicationsScienceGeoscienceCategory = _debian_category("Applications/Science/Geoscience", "Education")
ApplicationsScienceMathematicsCategory = _debian_category("Applications/Science/Mathematics", "Education")
ApplicationsScienceMedicineCategory = _debian_category("Applications/Science/Medicine", "Education")
ApplicationsSciencePhysicsCategory = _debian_category("Applications/Science/Physics", "Education")
ApplicationsScienceSocialCategory = _debian_category("Applications/Science/Social", "Education")
ApplicationsShellsCategory = _debian_category("Applications/Shells", "System")
ApplicationsSoundsCategory = _debian_category("Applications/Sound", "AudioVideo")
ApplicationsSystemCategory = _debian_category("Applications/System", "System")
ApplicationsSystemAdministrationCategory = _debian_category("Applications/System/Administration", "System")
ApplicationsSystemHardwareCategory = _debian_category("Applications/System/Hardware", "System")
ApplicationsSystemLanguageenvironmentCategory = _debian_category("Applications/System/Language Environment", "System")
ApplicationsSystemMonitoringCategory = _debian_category("Applications/System/Monitoring", "System")
ApplicationsSystemPackagemanagementCategory = _debian_category("Applications/System/Package Management", "System")
ApplicationsSystemSecurityCategory = _debian_category("Applications/System/Security", "System")
ApplicationsTerminalemulatorsCategory = _debian_category("Applications/Terminal Emulators", "System")
ApplicationsTextCategory = _debian_category("Applications/Text", "Utility")
ApplicationsTvandradioCategory = _debian_category("Applications/TV and Radio", "AudioVideo")
ApplicationsViewersCategory = _debian_category("Applications/Viewers", "Utility")
ApplicationsVideoCategory = _debian_category("Applications/Video", "AudioVideo")
ApplicationsWebdevelopmentCategory = _debian_category("Applications/Web Development", "Development")
GamesActionCategory = _debian_category("Games/Action", "Game")
GamesAdventureCategory = _debian_category("Games/Adventure", "Game")
GamesBlocksCategory = _debian_category("Games/Blocks", "Game")
GamesBoardCategory = _debian_category("Games/Board", "Game")
GamesCardCategory = _debian_category("Games/Card", "Game")
GamesPuzzlesCategory = _debian_category("Games/Puzzles", "Game")
GamesSimulationCategory = _debian_category("Games/Simulation", "Game")
GamesStrategyCategory = _debian_category("Games/Strategy", "Game")
GamesToolsCategory = _debian_category("Games/Tools", "Game")
GamesToysCategory = _debian_category("Games/Toys", "Game")
HelpCategory = _debian_category("Help", "System")
ScreenSavingCategory = _debian_category("Screen/Saving", "System")
ScreenLockingCategory = _debian_category("Screen/Locking", "System")


class Section:

    def __init__(self, *, name):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name


def _debian_section(name: str) -> t.Type[Section]:
    class ASection(Section):
        def __init__(self):
            super().__init__(name=name)
    return ASection


AdministrationUtilitiesSection = _debian_section("admin")
MonoCliSection = _debian_section("cli-mono")
CommunicationProgramsSection = _debian_section("comm")
DatabasesSection = _debian_section("database")
DebianInstallerUdebPackagesSection = _debian_section("debian-installer")
DebugPackagesSection = _debian_section("debug")
DevelopmentSection = _debian_section("devel")
DocumentationSection = _debian_section("doc")
EditorsSection = _debian_section("editors")
EducationSection = _debian_section("education")
ElectronicsSection = _debian_section("electronics")
EmbeddedSoftwareSection = _debian_section("embedded")
FontsSection = _debian_section("fonts")
GamesSection = _debian_section("games")
GnomeSection = _debian_section("gnome")
GnuRSection = _debian_section("gnu-r")
GnustepSection = _debian_section("gnustep")
GraphicsSection = _debian_section("graphics")
HamRadioSection = _debian_section("hamradio")
HaskellSection = _debian_section("haskell")
WebServersSection = _debian_section("httpd")
InterpretersSection = _debian_section("interpreters")
IntrospectionSection = _debian_section("introspection")
JavaSection = _debian_section("java")
JavascriptSection = _debian_section("javascript")
KdeSection = _debian_section("kde")
KernelsSection = _debian_section("kernel")
LibraryDevelopmentSection = _debian_section("libdevel")
LibrariesSection = _debian_section("libs")
LispSection = _debian_section("lisp")
LanguagePacksSection = _debian_section("localization")
MailSection = _debian_section("mail")
MathematicsSection = _debian_section("math")
MetaPackagesSection = _debian_section("metapackages")
MiscellaneousSection = _debian_section("misc")
NetworkSection = _debian_section("net")
NewsgroupsSection = _debian_section("news")
OcamlSection = _debian_section("ocaml")
OldLibrariesSection = _debian_section("oldlibs")
OtherOSsAndFSsSection = _debian_section("otherosfs")
PerlSection = _debian_section("perl")
PhpSection = _debian_section("php")
PythonSection = _debian_section("python")
RubySection = _debian_section("ruby")
RustSection = _debian_section("rust")
ScienceSection = _debian_section("science")
ShellsSection = _debian_section("shells")
SoundSection = _debian_section("sound")
TasksSection = _debian_section("tasks")
TexSection = _debian_section("tex")
TextProcessingSection = _debian_section("text")
UtilitiesSection = _debian_section("utils")
VersionControlSystemsSection = _debian_section("vcs")
VideoSection = _debian_section("video")
VirtualPackagesSection = _debian_section("virtual")
WebSoftwareSection = _debian_section("web")
XWindowSystemSoftwareSection = _debian_section("x11")
XfceSection = _debian_section("xfce")
ZopePloneFrameworkSection = _debian_section("zope")


class ServiceDescription:
    """
    Description for Debian services to be included in a package.
    """

    def __init__(self, name: str, command: str):
        """
        :param name: The display name.
        :param command: The command to be executed.
        """
        self.name = name
        self.command = command


class Package(annize.fs.FilesystemContent):

    @annize.object.explicit_only("documentation")
    def __init__(self, *, source: annize.fs.FilesystemContent, menuentries: list[MenuEntry],
                 executable_links: list[ExecutableLink],
                 packagename: str|None, description: annize.i18n.TrStr|None,
                 summary: annize.i18n.TrStr|None,
                 section: Section|None,
                 homepage_url: str|None,
                 version: annize.data.Version|None,
                 documentation: annize.fs.FilesystemContent|None,
                 authors: list[annize.features.authors.Author],
                 prerm: str = "", postinst: str = "", architecture: str = "all"):
        super().__init__(self._path)
        self.__source = source
        self.__menuentries = menuentries
        self.__executable_links = executable_links
        self.__packagename = packagename
        self.__description = description
        self.__summary = summary
        self.__section = section
        self.__homepage_url = homepage_url
        self.__version = version
        self.__documentation = documentation
        self.__authors = authors
        self.__prerm = prerm
        self.__postinst = postinst
        self.__architecture = architecture

    def _path(self):
        with annize.i18n.culture_by_spec("en"):  # TODO zz
            return self._mkpackage(self._BuildInfo(
                source=self.__source, executable_links=self.__executable_links,
                name=self.__packagename or annize.features.base.project_name(), version=self.__version,
                description=str(self.__description or annize.features.base.long_description()),
                homepage=self.__homepage_url or annize.features.base.homepage_url(),
                author=annize.features.authors.join_authors(self.__authors or annize.features.authors.project_authors()),
                licensename="TODO zz",
                summary=str(self.__summary or annize.features.base.summary()),
                section=self.__section, menuentries=self.__menuentries or [], services=[],
                documentation_source=self.__documentation,
                prerm=self.__prerm, postinst=self.__postinst, architecture=self.__architecture)).path()

    @dataclasses.dataclass
    class _BuildInfo:
        source: annize.fs.FilesystemContent
        # TODO zz dependencies: "Optional[List['dependencies.Dependency']]" = None
        executable_links: list[ExecutableLink]
        menuentries: list[MenuEntry]
        services: list[ServiceDescription]
        description: str
        name: str
        version: annize.data.Version
        homepage: str
        author: annize.features.authors.Author
        licensename: str
        section: Section|None
        summary: str
        documentation_source: annize.fs.FilesystemContent|None
        prerm: str
        postinst: str
        architecture: str
        authorstring: str = None
        pkgrootpath: str = None#TODO     ALL PATHs:use FsEntry'?
        pkgpath_debian: str = None
        pkgpath_documentation: str = None
        pkgpath_pixmaps: str = None
        pkgpath_usrbin: str = None
        config_files: list[str] = None
        pkgsize: int = None
        result: annize.fs.FilesystemContent = None

    @classmethod
    def _mkpackage(cls, build: _BuildInfo) -> annize.fs.FilesystemContent:
        with annize.fs.fresh_temp_directory() as tmpdir:
            """#TODO noh
            if .utils.basic.call("fakeroot -v", shell=True)[0] != 0:
                raise .framework.exceptions.RequirementsMissingError("'fakeroot' seems to be unavailable")
            if .utils.basic.call("dpkg --version", shell=True)[0] != 0:
                raise .framework.exceptions.RequirementsMissingError("'dpkg' seems to be unavailable")
            """
            cls._mkpackage_prepareinfos(build, tmpdir)
            cls._mkpackage_mkcopyright(build)
            cls._mkpackage_mkchangelog(build)
            cls._mkpackage_mkexeclinks(build)
            cls._mkpackage_mkmenuentries(build)
            cls._mkpackage_mkservices(build)
            cls._mkpackage_determinesize(build)
            cls._mkpackage_mkprepostcmds(build)
            cls._mkpackage_mkdebiancontrolfile(build)
            cls._mkpackage_mkdebianconffilesfile(build)
            cls._mkpackage_correctbuildsourcepermissions(build)
            cls._mkpackage_dpkg(build)
            return build.result

    @classmethod
    def _mkpackage_prepareinfos(cls, build: _BuildInfo, tmpdir: annize.fs.TInputPath) -> None:
        sauxversion = f"-{build.version}" if build.version else ""
        packagerootname = f"{build.name}{sauxversion}-{build.architecture}"
        build.authorstring = f"{build.author.full_name} <{build.author.email or 'unknown@unknown'}>"
        build.pkgrootpath = f"{tmpdir}/{packagerootname}"
        build.pkgpath_debian = "/DEBIAN"
        build.pkgpath_documentation = f"/usr/share/doc/{build.name}"
        build.pkgpath_pixmaps = "/usr/share/pixmaps"
        build.pkgpath_usrbin = "/usr/bin"
        pkgrootpathfs = annize.fs.Path(build.pkgrootpath)  # TODO move inside 'build'
        build.source.path().copy_to(pkgrootpathfs)
        docdst = pkgrootpathfs(build.pkgpath_documentation)
        build.documentation_source.path().copy_to(docdst, destination_as_parent=True)
        for pkgpath in [build.pkgpath_debian, build.pkgpath_documentation, build.pkgpath_pixmaps, build.pkgpath_usrbin]:
            os.makedirs(f"{build.pkgrootpath}/{pkgpath}", exist_ok=True)
        build.config_files = []

    @classmethod
    def _mkpackage_mkcopyright(cls, build: _BuildInfo) -> None:
        copyrighttext = f"""
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {build.name}
Source: {build.homepage or ''}
Upstream-Contact: {build.authorstring}

Files: *
Copyright: {datetime.datetime.now().strftime("%Y")} {build.author.full_name}
License: {build.licensename}
        """[1:]
        for fdest in [f"{build.pkgpath_debian}/copyright", f"{build.pkgpath_documentation}/copyright"]:
            with open(f"{build.pkgrootpath}/{fdest}", "w") as f:
                f.write(copyrighttext)

    @classmethod
    def _mkpackage_mkchangelog(cls, build: _BuildInfo) -> None:
        with open(f"{build.pkgrootpath}/{build.pkgpath_documentation}/changelog.gz", "wb") as f:
            f.write(gzip.compress(f"""
{build.name} {build.version or '1.0'} unstable; urgency=low

* New upstream release.
* See website for details.

-- {build.authorstring}  Mon, 14 Jan 2013 13:37:00 +0000
        """[1:].encode("utf-8")))

    @classmethod
    def _mkpackage_mkexeclinks(cls, build: _BuildInfo) -> None:
        for executable_link in build.executable_links:
            os.symlink(executable_link.path, f"{build.pkgrootpath}/{build.pkgpath_usrbin}/{executable_link.name}")

    @classmethod
    def _mkpackage_mkmenuentries(cls, build: _BuildInfo) -> None:
        def escapecmd(cmd):
            return cmd.replace('"', '\\"')
        os.makedirs(f"{build.pkgrootpath}/usr/share/menu")
        os.makedirs(f"{build.pkgrootpath}/usr/share/applications")
        for menuentry in build.menuentries:
            if menuentry.icon:
                iconfname = f"{build.name}.{menuentry.name}.png"
                icondstroot = annize.fs.Path(build.pkgrootpath)
                icondst = icondstroot(build.pkgpath_pixmaps)(iconfname)
                menuentry.icon.path().copy_to(icondst)
                sdebianiconspec = f'icon="/usr/share/pixmaps/{iconfname}"'
                sfreedesktopiconspec = f"Icon=/usr/share/pixmaps/{iconfname}"
            else:
                sdebianiconspec = sfreedesktopiconspec = ""
            with open(f"{build.pkgrootpath}/usr/share/menu/{menuentry.name}", "w") as f:
                sdebianneeds = "X11" if menuentry.is_gui else "text"
                f.write(f'?package({menuentry.name}):'
                        f'  command="{escapecmd(menuentry.command)}"'
                        f'  needs="{sdebianneeds}"'
                        f'  section="{menuentry.category.debian_name}"'
                        f'  title="{menuentry.title}"'
                        f'  {sdebianiconspec}\n')
            with open(f"{build.pkgrootpath}/usr/share/applications/{menuentry.name}.desktop", "w") as f:
                f.write(f"[Desktop Entry]\n"
                        f"Name={menuentry.title}\n"
                        f"Exec={menuentry.command}\n"
                        f"Terminal={'false' if menuentry.is_gui else 'true'}\n"
                        f"Type=Application\n"
                        f"Categories={menuentry.category.freedesktop_name};\n"
                        f"{sfreedesktopiconspec}\n")

    @classmethod
    def _mkpackage_mkservices(cls, build: _BuildInfo) -> None:
        os.makedirs(f"{build.pkgrootpath}/etc/init")
        startservicescall = ""
        stopservicescall = ""
        for service in build.services:
            servicename = service.name
            servicecommand = service.command
            with open(f"{build.pkgrootpath}/etc/init/{servicename}.conf", "w") as f:  # TODO systemd services
                f.write(f"""
# {build.name} - {build.name} job file

description "{build.name} service '{servicename}'"
author "{build.authorstring}"

start on runlevel [2345]

stop on runlevel [016]

exec {servicecommand}
        """[1:])
            build.postinst = f"{build.postinst}\nservice {servicename} start"
            build.prerm = f"service {servicename} stop &>/dev/null || true\n{build.prerm}"
            build.config_files.append(f"/etc/init/{servicename}.conf")

    @classmethod
    def _mkpackage_determinesize(cls, build: _BuildInfo) -> None:
        size = 0
        for dirpath, dirnames, filenames in os.walk(build.pkgrootpath):
            for f in filenames:
                ff = f"{dirpath}/{f}"
                if not os.path.islink(ff):
                    size += os.path.getsize(ff)
        build.pkgsize = size

    @classmethod
    def _mkpackage_mkprepostcmds(cls, build: _BuildInfo) -> None:
        fdebian = f"{build.pkgrootpath}/{build.pkgpath_debian}"
        with open(f"{fdebian}/prerm", "w") as f:
            f.write(f"#!/bin/bash\n"
                    f"set -e\n"
                    f"{build.prerm}\n")
        with open(f"{fdebian}/postinst", "w") as f:
            f.write(f"#!/bin/bash\n"
                    f"set -e\n"
                    f"{build.postinst}\n"
                    f"if test -x /usr/bin/update-menus; then update-menus; fi\n")

    @classmethod
    def _mkpackage_mkdebiancontrolfile(cls, build: _BuildInfo) -> None:
        dependencies = [] #TODO build.dependencies
        reqdependencies = [x for x in dependencies if isinstance(x.kind, annize.features.dependencies.common.Required)]
        recdependencies = [x for x in dependencies if isinstance(x.kind, annize.features.dependencies.common.Recommended)]
        sugdependencies = []  # TODO
        sdepends = ("\nDepends: " + (", ".join(reqdependencies))) if len(reqdependencies) > 0 else ""
        srecommends = ("\nRecommends: " + (", ".join(recdependencies))) \
            if len(recdependencies) > 0 else ""
        ssuggests = ("\nSuggests: " + (", ".join(sugdependencies))) if len(sugdependencies) > 0 else ""
        sdescription = "\n".join([" " + x for x in (build.description or "").split("\n") if x.strip() != ""])
        with open(f"{build.pkgrootpath}/{build.pkgpath_debian}/control", "w") as f:
            f.write(f"""
Package: {build.name}
Version: {build.version or '1.0'}
Section: {(build.section or MiscellaneousSection()).name}
Priority: optional
Architecture: {build.architecture}{sdepends}{srecommends}{ssuggests}
Installed-Size: {int(math.ceil(build.pkgsize / 1024.))}
Maintainer: {build.authorstring}
Provides: {build.name}
Homepage: {build.homepage or ''}
Description: {build.summary}
{sdescription}
"""[1:])

    @classmethod
    def _mkpackage_mkdebianconffilesfile(cls, build: _BuildInfo) -> None:
        with open(f"{build.pkgrootpath}/{build.pkgpath_debian}/conffiles", "w") as f:
            f.write("\n".join(build.config_files))

    @classmethod
    def _mkpackage_correctbuildsourcepermissions(cls, build: _BuildInfo) -> None:
        subprocess.check_call(["chmod", "-R", "u+rw,g+r,g-w,o+r,o-w", build.pkgrootpath])
        subprocess.check_call(["chmod", "-R", "0755", f"{build.pkgrootpath}/{build.pkgpath_debian}"])
        subprocess.check_call(["chmod", "0644", f"{build.pkgrootpath}/{build.pkgpath_debian}/conffiles"])

    @classmethod
    def _mkpackage_dpkg(cls, build: _BuildInfo) -> None:
        sauxversion = f"_{build.version}" if build.version else ""
        debfilename = f"{build.name}{sauxversion}_{build.architecture}.deb"
        result = annize.fs.fresh_temp_directory()
        subprocess.check_call(["fakeroot", "dpkg", "-b", build.pkgrootpath, f"{result.path}/{debfilename}"])
        build.result = result.path(debfilename)
