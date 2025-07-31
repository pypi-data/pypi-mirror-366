# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Internationalization, i.e. translation and similar tasks.
"""
import typing as t

import annize.flow.run_context
import annize.data
import annize.i18n


class _ProjectDefinedTranslationProvider(annize.i18n.TranslationProvider):
    """
    Internally created translation provider for backing :py:class:`String` instances.
    """

    def __init__(self):
        self.__translations = {}

    def __translations_for_string_name(self, string_name: str) -> dict[str, str]:
        result = self.__translations[string_name] = self.__translations.get(string_name) or {}
        return result

    def translate(self, string_name, *, culture):
        return self.__translations_for_string_name(string_name).get(culture.iso_639_1_language_code)

    def add_translations(self, string_name: str, variants: dict[str, str]) -> None:
        self.__translations_for_string_name(string_name).update(variants)


_translation_provider = _ProjectDefinedTranslationProvider()

annize.i18n.add_translation_provider(_translation_provider, priority=-100_000) # TODO who unloads it?!


class String(annize.i18n.ProvidedTrStr):
    """
    A translatable text defined in an Annize project.
    """

    def __init__(self, *, string_name: str|None, stringtr: str|None, **variants: str):
        if stringtr:
            stringtr = stringtr.strip()
            if not stringtr.endswith(")"):
                raise ValueError("stringtr specification must end with ')'")
            istart = stringtr.find("(")
            if istart == -1:
                raise ValueError("stringtr specification must contain a '('")
            inrstr = stringtr[istart+1:-1].strip()
            if (len(inrstr) < 3) or (inrstr[0] != inrstr[-1]) or (inrstr[0] not in ["'", '"']):
                raise ValueError("stringtr specification must contain a gettext text id inside quotes")
            string_name = inrstr[1:-1]
        if not string_name:
            string_name = annize.data.UniqueId().long_str
        super().__init__(string_name)
        if variants:
            _translation_provider.add_translations(string_name, variants)


class Culture(annize.i18n.Culture):
    """
    A culture defined in an Annize project.
    """

    def __init__(self, *, iso_639_1_language_code: str, region_code: str|None,
                 fallback_cultures: list[annize.i18n.Culture]):
        # TODO weird
        TODO = annize.i18n.culture_by_spec(iso_639_1_language_code).english_lang_name  # TODO region_code
        super().__init__(TODO, iso_639_1_language_code=iso_639_1_language_code, region_code=region_code,
                         fallback_cultures=fallback_cultures)


class ProjectCultures(list):
    """
    Definition of an Annize project's target cultures.
    """

    def __init__(self, *, cultures: list[annize.i18n.Culture]):
        super().__init__(cultures)


def project_cultures() -> t.Sequence[annize.i18n.Culture]:
    """
    Return a list of the current Annize project's target cultures. See also :py:class:`ProjectCultures`.
    """
    return tuple(culture
                 for cultures in annize.flow.run_context.objects_by_type(ProjectCultures)
                 for culture in cultures)
