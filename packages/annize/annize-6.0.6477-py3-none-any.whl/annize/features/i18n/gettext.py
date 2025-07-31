# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
gettext-based internationalization.
"""
import os
import subprocess

import annize.features.base
import annize.features.i18n.common
import annize.fs
import annize.i18n


class UpdatePOs:

    def __init__(self, *, po_directory: annize.fs.TInputPath):
        self.__po_directory = annize.fs.content(po_directory)

    def __call__(self, *args, **kwargs):
        #import time; time.sleep(5)#TODO
        #import annize.user_feedback; xx= annize.user_feedback.message_dialog("fuh!", ["bar", "baz"], config_key="füze");yy= annize.user_feedback.input_dialog(f"describ {xx}", suggested_answer=str(xx));annize.user_feedback.message_dialog(f"you has {yy}!", ["oke"]) #TODO

        po_directory = self.__po_directory.path()
        srcdir = annize.fs.Path(annize.features.base.project_directory())
        allfiles = []
        for dirtup in os.walk(srcdir):
            for f in dirtup[2]:
                ff = f"{dirtup[0]}/{f}"
                if [suf for suf in [".py", ".ui", ".xml", ".js", ".c", ".cpp", ".h", ".hpp"] if ff.endswith(suf)]:
                    allfiles.append(ff)  # TODO  arg list gets very long
        with annize.fs.fresh_temp_directory() as tmpdir:
            pot_file = tmpdir("pot.pot")
            subprocess.check_call(["xgettext", "--keyword=tr", "--add-comments", "--from-code", "utf-8", "--sort-output", "-o", pot_file, *allfiles])
            for fpofile in set((*po_directory.iterdir(),
                               *(po_directory(f"{culture.full_name}.po") for culture in annize.features.i18n.common.project_cultures()))):  # TODO zz only *.po ?!
                if not fpofile.exists():
                    fpofile.touch()
                subprocess.check_call(["msgmerge", "--no-fuzzy-matching", "--backup=none", "--update", fpofile, pot_file])


class GenerateMOs:

    def __init__(self, *, po_directory: annize.fs.TFilesystemContent, mo_directory: annize.fs.TInputPath, file_name: str|None):
        self.__po_directory = annize.fs.content(po_directory)
        self.__mo_directory = annize.fs.content(mo_directory)
        self.__file_name = file_name

    def __call__(self, *args, **kwargs):
        # TODO zz
        file_name = self.__file_name or annize.features.base.project_name()
        po_dir = self.__po_directory.path()
        mos_dir = self.__mo_directory.path()
        for po_file in os.listdir(po_dir):
            outdir = f"{mos_dir}/{po_file[:-3]}/LC_MESSAGES"
            os.makedirs(outdir, exist_ok=True)
            subprocess.check_call(["msgfmt", f"--output-file={outdir}/{file_name}.mo", f"{po_dir}/{po_file}"])


class TextSource:

    def __init__(self, *, mo_directory: annize.fs.TInputPath, priority: int = 0):
        mo_directory = annize.fs.content(mo_directory).path()
        annize.i18n.add_translation_provider(annize.i18n.GettextTranslationProvider(mo_directory), priority=priority)
