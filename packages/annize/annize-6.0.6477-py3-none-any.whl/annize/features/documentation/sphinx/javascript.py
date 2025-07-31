# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based Javascript documentation.
"""
import codecs
import glob
import json
import subprocess
import tempfile
import typing as t

import annize.features.documentation.sphinx.common

# pylint: disable=undefined-variable ## TODO weg


class JavaScriptApiReferenceLanguage(annize.features.documentation.sphinx.common.ApiReferenceLanguage):
    """
    JavaScript language support for api references.
    """

    def __jsfiles(self, dirf: str) -> list[str]:
        return glob.glob(f"{dirf}/**/*.js", recursive=True)

    def __scanjsfile(self, f: str) -> str:
        res = ""
        with codecs.getwriter("utf-8")(tempfile.TemporaryFile(mode="w+b")) as ftmp:
            subprocess.Popen(["jsdoc", "-X", f], stdout=ftmp).wait()
            ftmp.seek(0)
            for jto in json.loads(ftmp.read()):
                name = jto.get("name", "")
                if (not name.startswith("__")) and (jto.get("scope", "") == "global") and \
                        (not jto.get("undocumented", False)):
                    if jto["kind"] == "class":
                        res += (f".. js:autoclass:: {name}\n"
                                f"   :members:\n\n")
                    elif jto["kind"] == "function":
                        res += f".. js:autofunction:: {name}\n\n"
        return res

    def generate_sources(self, rgeninfo):
        super().generate_sources(srcpath, outpath, confdirpath, heading)
        cnt = docgen.heading(heading)
        for jsfile in self.__jsfiles(outpath):
            cnt += self.__scanjsfile(jsfile)
        with open(f"{outpath}.rst", "w") as f:
            f.write(cnt)
        annize.utils.basic.verify_tool_installed("jsdoc")
        returnconfig = (f"extensions.append('sphinx_js')\n"
                        f"js_source_path = {repr(outpath)}\n")
