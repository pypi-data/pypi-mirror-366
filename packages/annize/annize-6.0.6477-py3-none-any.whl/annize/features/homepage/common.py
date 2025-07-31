# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Homepage.
"""
import abc
import dataclasses
import typing as t

import annize.flow.run_context
import annize.features.base
import annize.features.changelog.common
import annize.features.dependencies.common
import annize.features.documentation.common
import annize.features.documentation.sphinx.common
import annize.features.documentation.sphinx.output.html
import annize.features.documentation.sphinx.rst
import annize.features.distributables.common
import annize.features.i18n.common
import annize.features.media_galleries
import annize.fs
import annize.i18n


class HomepageSection(abc.ABC):

    @dataclasses.dataclass
    class _GenerateInfo:
        culture: annize.i18n.Culture
        custom_arg: object|None
        document_root_url: str
        document_variant_directory: annize.fs.Path
        document_variant_url: str

    @dataclasses.dataclass
    class _PrePostProcGenerateInfo:
        document_root_directory: annize.fs.Path
        document_root_url: str
        custom_arg: object|None

    class Content:

        def __init__(self, *, rst_text: str = "", media_files: list[annize.fs.FilesystemContent] = ()):
            self.__rst_text = rst_text or ""
            self.__media_files = list(media_files or ())

        @property
        def rst_text(self) -> str:
            return self.__rst_text

        @property
        def media_files(self) -> list[annize.fs.FilesystemContent]:
            return self.__media_files

        def append_rst(self, rst_text) -> None:
            self.__rst_text += rst_text + "\n\n"

        def attach_media_file(self, file: annize.fs.FilesystemContent) -> None:
            self.__media_files.append(file)

    def __init__(self, *, head: annize.i18n.TrStr, sort_index: int = 0):
        self.__head = head
        self.__sort_index = sort_index

    @property
    def head(self) -> annize.i18n.TrStr:
        return self.__head

    @property
    def sort_index(self) -> int:
        return self.__sort_index

    def pre_process_generate(self, info: _PrePostProcGenerateInfo) -> None:
        pass

    @abc.abstractmethod
    def generate_content(self, info: _GenerateInfo) -> Content:
        pass

    def post_process_generate(self, info: _PrePostProcGenerateInfo) -> None:
        pass


class Homepage:

    def __init__(self, *, title: annize.i18n.TrStr|None, short_desc: annize.i18n.TrStr|None,
                 sections: list[HomepageSection], cultures: list[annize.i18n.Culture]):
        self.__title = title
        self.__short_desc = short_desc
        self.__sections = sections
        self.__cultures = cultures

    @property
    def cultures(self) -> list[annize.i18n.Culture]:
        return self.__cultures or annize.features.i18n.common.project_cultures() or [annize.i18n.unspecified_culture]

    @property
    def sections(self) -> list[HomepageSection]:
        return self.__sections

    @property
    def title(self) -> annize.i18n.TrStr:
        return self.__title or annize.features.base.pretty_project_name()

    @property
    def short_desc(self) -> annize.i18n.TrStr:
        return self.__short_desc or annize.features.base.summary()

    def _append_section(self, section: HomepageSection) -> None:
        self.__sections.append(section)

    def generate(self):
        variants = []
        sections = sorted(self.sections, key=lambda x: x.sort_index)
        result = annize.fs.fresh_temp_directory(annize.flow.run_context.object_name(self)).path
        custom_args = {section: None for section in sections}
        document_root_url = "../"  # TODO nicer?! more robust?!
        self.__generate_pre_post_proc(custom_args=custom_args, is_pre=True,
                                    document_root_directory=result,
                                    document_root_url=document_root_url)
        rm_custom_args = set()
        for culture in self.cultures:
            document_variant_directory = result(culture.full_name)
            with culture:
                page = annize.features.documentation.sphinx.rst.RstGenerator.heading(self.title)  # heading won't be visible
                for section in sections:
                    pcont = self.__generate_section(section, custom_args=custom_args,
                                                    culture=culture,
                                                    document_root_directory=result, document_root_url=document_root_url,
                                                    document_variant_directory=document_variant_directory)
                    if not pcont:
                        rm_custom_args.add(section)
                    page += pcont
                fpage = annize.fs.dynamic_file(content=page, file_name="index.rst")
                variants.append(annize.features.documentation.sphinx.common.RstDocumentVariant(culture=culture,#TODO
                                                                                               source=fpage))
        for rm_custom_arg in rm_custom_args:
            custom_args.pop(rm_custom_arg)
        doc = annize.features.documentation.sphinx.common.RstDocument(variants=variants,
                                      project_name=self.title, version=None, release=None, authors=None, title=self.title  #TODO
                                                                      )
        output_spec = annize.features.documentation.sphinx.output.html.HtmlOutputSpec(short_desc=self.short_desc,
                                                                                     is_homepage=True)
        doc.generate_all_cultures(output_spec).file.path().move_to(result, merge=True)
        self.__generate_pre_post_proc(custom_args=custom_args, is_pre=False,
                                    document_root_directory=result,
                                    document_root_url=document_root_url)
        return result

    @staticmethod
    def __generate_pre_post_proc(*, custom_args: dict, is_pre: bool,
                               document_root_directory: annize.fs.Path, document_root_url: str):
        for section, custom_arg in custom_args.items():
            prepostprocinfo = HomepageSection._PrePostProcGenerateInfo(
                custom_arg=custom_arg, document_root_directory=document_root_directory,
                document_root_url=document_root_url)
            (section.pre_process_generate if is_pre else section.post_process_generate)(prepostprocinfo)
            custom_args[section] = prepostprocinfo.custom_arg

    @staticmethod
    def __generate_section(section, *, custom_args: dict, culture: annize.i18n.Culture,
                           document_root_directory: annize.fs.Path, document_root_url: str,
                           document_variant_directory: annize.fs.Path):
        document_variant_directory.mkdir(exist_ok=True)
        generate_info = HomepageSection._GenerateInfo(
            culture=culture, custom_arg=custom_args[section],
            document_root_url=document_root_url, document_variant_url="",
            document_variant_directory=document_variant_directory)
        section_content = section.generate_content(generate_info)
        if section_content is not None:
            custom_args[section] = generate_info.custom_arg
            heading_rst = annize.features.documentation.sphinx.rst.RstGenerator.heading(section.head,
                                                                                        variant="^", sub=True,
                                                                                        anchor="TODO sctn.key")
            return f"{heading_rst}\n{section_content.rst_text}\n\n"
        return ""


class SimpleProjectHomepage(Homepage):

    def __init__(self, *, changelog: annize.features.changelog.common.Changelog|None,
                 dependencies: list[annize.features.dependencies.common.Dependency],
                 distributables: list[annize.features.distributables.common.Group],
                 documentation: list[annize.features.documentation.common.Document],
                 imprint: annize.i18n.TrStr|None,
                 media_galleries: list[annize.features.media_galleries.Gallery], **kwargs):
        import annize.features.homepage.sections.about
        import annize.features.homepage.sections.changelog
        import annize.features.homepage.sections.documentation
        import annize.features.homepage.sections.download
        import annize.features.homepage.sections.gallery
        import annize.features.homepage.sections.imprint
        import annize.features.homepage.sections.license
        sections = annize.features.homepage.sections
        super().__init__(**kwargs)
        self._append_section(sections.about.Section())
        self._append_section(sections.changelog.Section(changelog=changelog))
        self._append_section(sections.documentation.Section(documentation=documentation))
        self._append_section(sections.download.Section(distributables=distributables, dependencies=dependencies))
        self._append_section(sections.gallery.Section(media_galleries=media_galleries))
        self._append_section(sections.imprint.Section(imprint=imprint))
        self._append_section(sections.license.Section())


class GeneratedHomepage(annize.fs.FilesystemContent):

    def __init__(self, *, homepage: Homepage):
        super().__init__(self._path)
        self.__homepage = homepage

    def _path(self):
        return self.__homepage.generate()


# TODO noh :     import locale; locale.setlocale(locale.LC_ALL, '')   ?!  see http://pythondialog.sourceforge.net/
