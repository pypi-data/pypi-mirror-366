# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based HTML documentation output.
"""
import html
import json
import typing as t

import annize.asset
import annize.features.base
import annize.features.documentation.common
import annize.features.documentation.sphinx.output.common
import annize.fs
import annize.i18n


class HtmlOutputSpec(annize.features.documentation.common.HtmlOutputSpec):

    #TODO
    def __init__(self, *, is_homepage: bool = False,
                 short_title: annize.i18n.TrStr|None = None,
                 short_desc: annize.i18n.TrStr|None = None, theme: str|None = None,
                 masterlink: str|None = None,
                 logo_image: annize.fs.TFilesystemContent|None = None,
                 background_image: annize.fs.TFilesystemContent|None = None):#TODO parameters useful here?
        """
        :param theme: The sphinx html theme name.
        :param short_title: The short html title.
        :param short_desc: The short description. Ignored by most themes.
        :param masterlink: Url that overrides the target of the main heading (which is also a link).
        """
        super().__init__(is_homepage=is_homepage)#TODO always just pass *args,**kwargs ?!
        self.__short_title = short_title
        self.__short_desc = short_desc
        self.__theme = theme
        self.__masterlink = masterlink#TODO weg hier?!
        self.__logo_image = logo_image
        self.__background_image = background_image

    @property
    def short_title(self) -> annize.i18n.TrStr|None:  # TODO move to `Document` (like `title`) ?! also others?!
        return self.__short_title

    @property
    def short_desc(self) -> annize.i18n.TrStr|None:
        return self.__short_desc

    @property
    def theme(self) -> str|None:
        return self.__theme

    @property
    def masterlink(self) -> str|None:
        return self.__masterlink

    @property
    def logo_image(self) -> annize.fs.FilesystemContent|None:
        return self.__logo_image

    @property
    def background_image(self) -> annize.fs.FilesystemContent|None:
        return self.__background_image


@annize.features.documentation.sphinx.output.common.register_output_generator
class HtmlOutputGenerator(annize.features.documentation.sphinx.output.common.OutputGenerator):
    """
    HTML documentation output.
    """

    @classmethod
    def is_compatible_for(cls, output_spec):
        return isinstance(output_spec, annize.features.documentation.common.HtmlOutputSpec)

    def formatname(self):
        return "html"

    def prepare_generate(self, geninfo):  # TODO geninfo.outdir weg?!
        geninfo.entry_path = f"{geninfo.configvalues['master_doc']}.html"
        title = annize.i18n.tr_if_trstr(geninfo.main_document.title)  # TODO getattr or title in base class
        is_homepage = self.output_spec.is_homepage
        if isinstance(self.output_spec, HtmlOutputSpec):
            masterlink = self.output_spec.masterlink
            short_title = annize.i18n.tr_if_trstr(self.output_spec.short_title)
            short_desc = annize.i18n.tr_if_trstr(self.output_spec.short_desc)
            theme = self.output_spec.theme
            logo_image = self.output_spec.logo_image.path() if self.output_spec.logo_image else None
            background_image = self.output_spec.background_image
        else:
            masterlink = None
            short_title = None
            short_desc = None
            theme = None
            logo_image = None
            background_image = None
        short_desc = str(short_desc or "")
        theme = theme or "pimpinella_anisum"
        geninfo.configvalues["html_theme"] = theme
        htmlthemepaths = geninfo.configvalues["html_theme_path"] = list(map(str, geninfo.configvalues.get("html_theme_path", [])))
        htmlthemepaths.append(str(annize.asset.data.data_dir))
        ato = dict(sidebartreesmall=not is_homepage, menusectionindicator=not is_homepage, shortdesc=short_desc)
        if short_title or title:
            geninfo.configvalues["html_short_title"] = short_title or title
        if title:
            geninfo.configvalues["html_title"] = title
        if masterlink:
            ato["masterlink"] = masterlink
        htmlstatpaths = geninfo.configvalues["html_static_path"] = list(map(str, geninfo.configvalues.get("html_static_path", [])))
        if theme == "pimpinella_anisum":
            geninfo.configvalues["html_css_files"] = html_css_files = []
            basecolor = annize.features.base.brand_color()

            # TODO hacks
            background_image = annize.features.base.project_directory()("media/background.png")  # TODO
            if not background_image.exists():
                background_image = background_image.parent("background.jpg")
            for logo_image in annize.features.base.project_directory()("media/logo").children():  # TODO
                if logo_image.name.endswith(".64.png"):
                    break


            if background_image:
                bgimagename = f"_annize_bgimage.{background_image.name}"
                bgimagecssdirfs = geninfo.intstruct(bgimagename)
                bgimagecssfs = bgimagecssdirfs(bgimagename)
                background_image.copy_to(bgimagecssfs)
                htmlstatpaths.append(str(bgimagecssdirfs))
                ato["bgimage"] = bgimagename  # TODO does that rlly work (on all dir levels)?!
            for bcaa in range(10):
                for bcab in range(10):
                    for bcac in range(20):
                        sbcac = "abcdefghijklmnopqrst"[bcac]
                        ncolor = basecolor.scalehue(brightness=(bcab+1)/10, saturation=(bcac+1)/10)
                        ato[f"brandingcolor_{sbcac}{bcaa}{bcab}"] = (  # TODO only some of them
                            f"rgb({ncolor.red * 255},{ncolor.green * 255},{ncolor.blue * 255},"
                            f"{(bcaa + 1) / 10})")
        if is_homepage:
            ato.update(sidebarhidelvl1=True, headhidelvl1=True, sidebarhidelvl3up=True, shorthtmltitle=True)
        # TODO weird
        htmlthemeopts = geninfo.configvalues["html_theme_options"] = geninfo.configvalues.get("html_theme_options", {})
        htmlthemeopts.update(ato)
        # TODO
        htmlstatpaths.append("/home/pino/projects/annize/src/annize/asset/_static/icons/docrender")
        if logo_image:
            geninfo.configvalues["html_logo"] = str(logo_image)

    def multilanguage_frame(self, document):  # TODO nicer place, nicer name, nicer way, ...
        result = super().multilanguage_frame(document)
        htmllinks = ""
        for language in result.culture_names:
            langname = annize.i18n.culture_by_spec(language).english_lang_name
            langentrypath = result.entry_path_for_language(language)
            htmllinks += f"<a href='{html.escape(langentrypath)}'>{html.escape(langname)}</a><br/>"
        languageentrypoints = {language: result.entry_path_for_language(language) for language in result.culture_names}
        # TODO generate via sphinx instead?!
        title = "document.title" #TODO re: document.title
        htitle = f"<title>{html.escape(str(title))}</title>" if title else ""
        result.file.path()("index.html").write_file(  # TODO odd (we write to what should be a source)
            f"<!DOCTYPE html>"
            f"<html>"
            f"<head>"
            f"<meta charset='utf-8'>{htitle}"
            f"<script>"
            f"var myLanguage = navigator.language;"
            f"var languageEntryPoints = {json.dumps(languageentrypoints)};"
            f"function trylang(c) {{"
            f"    var entrypoint = languageEntryPoints[c];"
            f"    if (entrypoint) {{"
            f"        document.location.href = entrypoint;"
            f"        return true;"
            f"    }}"
            f"}};"
            f"trylang(myLanguage) || trylang(myLanguage.substring(0,2)) || trylang('en') || trylang('?');"
            f"</script>"
            f"</head>"
            f"<body>"
            f"<h1>🗣 🌐 ❓</h1>"
            f"{htmllinks}"
            f"</body>"
            f"</html>")  # TODO what with language = "?" ?!
        result._set_entry_path("index.html")
        return result
