# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based documentation.
"""
import abc
import dataclasses
import datetime
import subprocess
import typing as t

import annize.asset
import annize.flow.run_context
import annize.data
import annize.features.authors
import annize.features.base
import annize.features.dependencies.common
import annize.features.documentation.common
import annize.features.documentation.sphinx.output.common
import annize.features.documentation.sphinx.output.html as _
import annize.features.documentation.sphinx.output.pdf as _
import annize.features.documentation.sphinx.output.plaintext as _
import annize.features.documentation.sphinx.rst
import annize.features.i18n.common
import annize.features.licensing
import annize.features.version
import annize.fs
import annize.i18n


# TODO convention for headers: https://lpn-doc-sphinx-primer.readthedocs.io/en/stable/concepts/heading.html


class Document(annize.features.documentation.common.Document, abc.ABC):

    @dataclasses.dataclass
    class GenerateInfo:
        main_document: "Document"
        intstruct: annize.fs.Path
        outdir: annize.fs.FilesystemContent
        confdir: annize.fs.FilesystemContent
        culture: annize.i18n.Culture
        configvalues: dict
        configlines: list
        entry_path: str = ""

        def _to_dict(self):
            return {key: getattr(self, key) for key in dir(self) if not key.startswith("_")}

    def __init__(self, *, project_name: annize.i18n.TrStr|None, title: annize.i18n.TrStr|None,
                 authors: list[annize.features.authors.Author], version: annize.data.Version|None,
                 release: annize.i18n.TrStr|None):
        super().__init__()
        self.__projectname = project_name
        self.__title = title
        self.__authors = authors
        self.__version = version
        self.__release = release

    @abc.abstractmethod
    def _generate_sources(self, geninfo: "Document.GenerateInfo") -> str:
        pass

    @property
    def projectname__original(self) -> annize.i18n.TrStr|None:
        return self.__projectname

    @property
    def project_name(self) -> annize.i18n.TrStr:
        return self.projectname__original \
               or annize.features.base.pretty_project_name() or annize.i18n.TrStr.tr("an_ThisProject")

    @property
    def title__original(self) -> annize.i18n.TrStr|None:
        return self.__title

    @property
    def title(self) -> annize.i18n.TrStr:  # TODO fix or docu: not all output formats will show it
        return self.title__original or self.project_name

    @property
    def authors(self) -> list[annize.features.authors.Author]:
        return self.__authors

    @property
    def version(self) -> annize.data.Version|None:
        return self.__version

    @property
    def release(self) -> annize.i18n.TrStr|None:
        return self.__release

    def generate_all_cultures(self, output_spec):
        generator = annize.features.documentation.sphinx.output.common.find_output_generator_for_outputspec(output_spec)
        return generator.multilanguage_frame(self)

    def generate(self, output_spec, *, culture=None):
        with culture or annize.i18n.current_culture() as culture:
            generator = annize.features.documentation.sphinx.output.common.find_output_generator_for_outputspec(
                output_spec)
            # TODO media dirs
            with annize.fs.fresh_temp_directory() as tconfdir:
                confdir = tconfdir
                with annize.fs.fresh_temp_directory() as tintstruct:
                    intstruct = tintstruct
                    outdir = annize.fs.fresh_temp_directory().path
                    geninfo = Document.GenerateInfo(self, intstruct, outdir, confdir, culture, {}, [])
                    self.__generate_set_misc(geninfo)
                    self.__generate_prepare_shortsnippets(geninfo)
                    self.__generate_prepare_annizeicons(geninfo)
                    self.__generate_set_culture(geninfo)
                    self.__generate_set_version_and_release(geninfo)
                    geninfo.configvalues["master_doc"] = self._generate_sources(geninfo)
                    if culture.iso_639_1_language_code:
                        geninfo.configvalues["language"] = culture.iso_639_1_language_code
                    author = annize.features.authors.join_authors(self.__authors
                                                                  or annize.features.authors.project_authors()).full_name
                    geninfo.configvalues["copyright"] = f"{datetime.datetime.now().year}, {author}"
                    generator.prepare_generate(geninfo)
                    with open(f"{confdir}/conf.py", "w") as f:
                        f.write(self.__generate_geninfo_to_confpy(geninfo))
                    # TODO error handling
                    subprocess.check_call(["sphinx-build", "-c", confdir, "-b", generator.formatname(),
                                           intstruct, outdir], stderr=subprocess.STDOUT)
            outdir = generator.postproc(outdir)
            return annize.features.documentation.common.DocumentGenerateResult(outdir, geninfo.entry_path)

    def __generate_set_misc(self, geninfo):
        geninfo.configvalues.update({
            "project": str(self.project_name or annize.features.base.pretty_project_name()),
            "nitpicky": True,
            "rst_epilog": "",
            "extensions": ["sphinx.ext.autosummary", "sphinx.ext.inheritance_diagram"],
            "autoclass_content": "both",
            "autodoc_typehints": "description",
            "text_sectionchars": "'*=-~\"+`'#^°_",
            "html_show_sphinx": False,
            "html_static_path": [],
            "html_theme_options": dict(),
            "html_sidebars": {"**": ["globaltoc.html", "searchbox.html"]},
            "latex_elements": {"preamble": "\\usepackage{enumitem}\\setlistdepth{99}"}
        })

    @staticmethod
    def __generate_prepare_shortsnippets(geninfo):
        shortsnippets = {}  # TODO
        substitutions = "\n".join([f".. |{k}| replace:: {v}" for k, v in shortsnippets.items()])
        geninfo.configvalues["rst_epilog"] += substitutions + "\n"

    @staticmethod
    def __generate_prepare_annizeicons(geninfo):
        annizeiconssrcfs = annize.fs.Path(annize.asset.data.icons_dir)
        annizeicons = [annizeiconfs.name[:-4] for annizeiconfs in annizeiconssrcfs.children()]
        substitutions = "\n".join([f".. |annizeicon_{icon}| image:: /_annize_icons/{icon}.png" for icon in annizeicons])
        geninfo.configvalues["rst_epilog"] += substitutions + "\n"
        annizeiconssrcfs.copy_to(geninfo.intstruct("_annize_icons"))

    @staticmethod
    def __generate_set_culture(geninfo):
        geninfo.configvalues["language"] = annize.i18n.current_culture().iso_639_1_language_code

    def __generate_set_version_and_release(self, geninfo):
        version = self.version
        if not version:
            projectversions = annize.features.version.project_versions()
            if len(projectversions) == 1:  # TODO dedup xyz
                version = projectversions[0]
        if version:
            geninfo.configvalues["version"] = str(version)
        release = self.release or version
        if release:
            geninfo.configvalues["release"] = str(release)

    @staticmethod
    def __generate_geninfo_to_confpy(geninfo):
        confpylines = [f"{confkey} = {value!r}" for confkey, value in geninfo.configvalues.items()]
        confpylines += geninfo.configlines
        return "import base64, json\n" + "\n".join(confpylines)


class CompositeDocument(Document):

    def __init__(self, *, documents: t.Iterable[Document], **kwargs):
        super().__init__(**kwargs)
        self.__documents = documents

    @staticmethod
    def __get_inner_generateinfo(geninfo: Document.GenerateInfo, innerdoc: Document):
        kwa = geninfo._to_dict()
        kwa["intstruct"] = geninfo.intstruct(annize.flow.run_context.object_name(innerdoc))
        return Document.GenerateInfo(**kwa)

    def _generate_sources(self, geninfo):
        toctree = (".. toctree::\n"
                   "    :glob:\n"
                   "\n")
        for document in self.__documents:
            igeninfo = self.__get_inner_generateinfo(geninfo, document)
            igeninfo.intstruct.mkdir(exist_ok=False)
            dname = document._generate_sources(igeninfo)
            toctree += f"    {annize.flow.run_context.object_name(document)}/{dname}\n"
        name = annize.flow.run_context.object_name(self)
        with open(f"{geninfo.intstruct}/{name}.rst", "w") as f:
            f.write(toctree)
        return name


class ApiReferenceLanguage(abc.ABC):
    """
    Base class for a programming language in api references. See :py:class:`ApiReferencePiece`.
    """

    class ApiReferenceGenerateInfo(Document.GenerateInfo):

        def __init__(self, geninfo: Document.GenerateInfo, source: annize.fs.FilesystemContent, heading: annize.i18n.TrStr):
            super().__init__(**geninfo._to_dict())
            self.__source = source
            self.__heading = heading

        @property
        def source(self) -> annize.fs.FilesystemContent:
            return self.__source

        @property
        def heading(self) -> annize.i18n.TrStr:
            return self.__heading

    @abc.abstractmethod
    def generate_sources(self, rgeninfo: "ApiReferenceLanguage.ApiReferenceGenerateInfo") -> str:
        pass


class ApiReferenceDocument(Document):
    """
    An api reference.
    """

    def __init__(self, *, language: ApiReferenceLanguage, heading: annize.i18n.TrStr|None,
                 source: annize.fs.TFilesystemContent, cultures: list[annize.i18n.Culture], **kwargs):
        super().__init__(**kwargs)
        self.__language = language
        self.__heading = heading or annize.i18n.TrStr.tr("an_Doc_APIRefTitle")
        self.__source = annize.fs.content(source)
        self.__cultures = tuple(cultures)

    def available_cultures(self):
        return self.__cultures or annize.features.i18n.common.project_cultures()

    def __get_refgeninfo(self, geninfo: Document.GenerateInfo):
        return ApiReferenceLanguage.ApiReferenceGenerateInfo(geninfo, self.__source, self.__heading)
        # TODO temp_clone ?!

    def _generate_sources(self, geninfo):
        geninfo.configlines.append(f"import sys; sys.path.append({repr(str(self.__source.path().parent))})")
        return self.__language.generate_sources(self.__get_refgeninfo(geninfo))


class ArgparseCommandLineInterfaceDocument(Document):

    def __init__(self, *, parser_factory: str, program_name: str, heading: str|None,
                 source_directory: annize.fs.TFilesystemContent, cultures: list[annize.i18n.Culture], **kwargs):
        super().__init__(**kwargs)
        self.__parser_factory = parser_factory
        self.__program_name = program_name
        self.__heading = heading or annize.i18n.TrStr.tr("an_Doc_CLIRefTitle")
        self.__source = annize.fs.content(source_directory)
        self.__cultures = tuple(cultures)

    def available_cultures(self):
        return self.__cultures or annize.features.i18n.common.project_cultures()

    def _generate_sources(self, geninfo):
        geninfo.configvalues["extensions"].append("sphinxarg.ext")
        #TODO intdst = geninfo.intstruct("TODO zz cliref")
        #TODO self.__source.copy_to(intdst)
        geninfo.configlines.append(f"import sys; sys.path.append({repr(str(self.__source.path()))})")
        toctree = (f".. argparse::\n"
                   f"    :ref: {self.__parser_factory}\n"
                   f"    :prog: {self.__program_name}\n")
        name = annize.flow.run_context.object_name(self)
        with open(f"{geninfo.intstruct}/{name}.rst", "w") as f:
            f.write(annize.features.documentation.sphinx.rst.RstGenerator.heading(self.__heading))#TODO
            f.write(toctree)
        return name


class RstDocumentVariant:

    def __init__(self, *, culture: annize.i18n.Culture = annize.i18n.unspecified_culture, source: annize.fs.TFilesystemContent):
        self.__culture = culture
        self.__source = annize.fs.content(source)

    @property
    def culture(self) -> annize.i18n.Culture:
        return self.__culture

    @property
    def source(self) -> annize.fs.FilesystemContent:
        return self.__source


class RstDocument(Document):
    """
    A reStructuredText formatted file or a directory of such files.
    """

    def available_cultures(self):
        return list(set(v.culture for v in self.__variants))

    def __init__(self, *, variants: list[RstDocumentVariant], **kwargs):
        super().__init__(**kwargs)
        self.__variants = variants

    def __get_variant(self, culture: annize.i18n.Culture) -> RstDocumentVariant|None:
        for variant in self.__variants:
            if variant.culture == culture:
                return variant
        return None

    def _generate_sources(self, geninfo):  # TODO cache it, so we can potentially remove source?!
        source = annize.fs.Path(self.__get_variant(geninfo.culture).source)
        basename = source.name
        if not basename.lower().endswith(".rst"):
            basename += ".rst"
        source.copy_to(geninfo.intstruct(basename))
        return basename[:-4]


class AboutProjectDocument(Document):

    def __init__(self, *, dependencies: list[annize.features.dependencies.common.Dependency],
                 cultures: list[annize.i18n.Culture], **kwargs):
        super().__init__(**kwargs)
        self.__dependencies = dependencies
        self.__cultures = tuple(cultures)

    def available_cultures(self):
        return self.__cultures or annize.features.i18n.common.project_cultures()

    def _generate_sources(self, geninfo):  # TODO review
        readmefs = geninfo.intstruct("readme.rst")
        head_about = annize.i18n.tr("an_Doc_ReadmeHeadAbout")
        head_license = annize.i18n.tr("an_Doc_ReadmeHeadLicense")
        head_uptodate = annize.i18n.tr("an_Doc_ReadmeHeadUpToDate")
        head_dependencies = annize.i18n.tr("an_Doc_ReadmeHeadDependencies")
        content_about = annize.features.base.long_description()
        licenses = annize.features.licensing.project_licenses()
        project_version = self.version
        if not project_version:
            project_versions = annize.features.version.project_versions()  # TODO dedup xyz
            project_version = project_versions[0]  # TODO
        dependencies = self.__dependencies or []  # TODO
        content = (f"{annize.features.documentation.sphinx.rst.RstGenerator.heading(head_about, sub=True)}"
                   f"{content_about}")
        project_name = self.project_name  # TODO i18n
        if len(licenses) > 0:
            license_names = annize.i18n.friendly_join_string_list([str(lic.name) for lic in licenses])
            content_license = annize.i18n.tr("an_HP_Lic_Text").format(**locals())
            content += (f"{annize.features.documentation.sphinx.rst.RstGenerator.heading(head_license)}"
                        f"{content_license}")
        content_uptodate = annize.i18n.tr("an_Doc_ReadmeUpToDate")
        if project_version:
            content_uptodate += " " + annize.i18n.tr("an_Doc_ReadmeUpToDateCurrentVersion").format(**locals())
        content += (f"{annize.features.documentation.sphinx.rst.RstGenerator.heading(head_uptodate)}"
                    f"{content_uptodate}")
        if len(dependencies) > 0:
            content_dependencies = annize.i18n.tr("an_HP_DL_Uses3rdParty").format(**locals())
            content_dependencies += "\n\n" + annize.features.dependencies.common.dependencies_to_rst_text(dependencies)
            content += (f"{annize.features.documentation.sphinx.rst.RstGenerator.heading(head_dependencies)}"
                        f"{content_dependencies}")
        readmefs.write_file(content)
        return "readme"


class ReadmeDocument(CompositeDocument):  # TODO noh maturity flags?!
    """
    A reStructuredText formatted file or a directory of such files.
    """

    _ABOUT_NAME = annize.data.UniqueId("about").processonly_long_str

    def __init__(self, *, project_name, title, authors, version, release, documents: t.Iterable[Document],
                 dependencies: list[annize.features.dependencies.common.Dependency],
                 cultures: list[annize.i18n.Culture]):
        aboutdocument = AboutProjectDocument(project_name=project_name, authors=authors, version=version,
                                             release=release, dependencies=dependencies, cultures=cultures, title=None)
        super().__init__(project_name=project_name, authors=authors, version=version, release=release, title=title,
                         documents=[aboutdocument, *documents])
        annize.flow.run_context.set_object_name(aboutdocument, self._ABOUT_NAME)
        self.__cultures = cultures

    def available_cultures(self):
        return self.__cultures or annize.features.i18n.common.project_cultures()

    @property
    def title(self):
        project_name = self.project_name
        return self.title__original or annize.i18n.TrStr.tr("an_Doc_ReadmeTitle").format(**locals())


"""TODO
manpage
template_bridge
https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html#module-sphinx.ext.autosummary
https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
""".upper().lower()

# TODO noh: fix all docstrings in documentation.* (some are old)
# TODO noh      f"exclude_patterns = ['.directory', 'Thumbs.db', '.DS_Store', '.git', '.svn', '.piget', '.idea']\n"
# TODO noh generalize .format(**locals) hacks on input strings from config ?!

