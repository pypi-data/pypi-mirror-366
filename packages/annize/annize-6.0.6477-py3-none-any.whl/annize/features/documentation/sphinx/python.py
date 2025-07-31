# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Sphinx-based Python documentation.
"""
import os
import subprocess

import annize.features.documentation.sphinx.common
import annize.features.documentation.sphinx.rst
import annize.fs


class Python3ApiReferenceLanguage(annize.features.documentation.sphinx.common.ApiReferenceLanguage):
    """
    Python 3 language support for api references.
    """

    def __patch_property_types_in_docstrings(self, pdir: str) -> None:  # TODO# remove this when Sphinx can do it better
        def patchfile(ffp):
            def patchprop(cnt, j):
                def moddocstr(propname, cnt, inxl, iind, rettype, sblk):
                    linsi = cnt.find(sblk, cnt.find(sblk, inxl)+1)
                    llinsi = cnt.rfind("\n", 0, linsi) + 1 + iind
                    issettable = f"@{propname}.setter" in cnt
                    alb = "\n" + (" "*iind)
                    return cnt[:llinsi] + alb + f":rtype: {rettype}" + \
                        (f"\n{alb}This property is also settable." if issettable else "") + alb + cnt[llinsi:]
                def insdocstr(propname, cnt, inxl, iind, rettype):
                    return moddocstr(propname, cnt[:inxl+iind] + 2 * ("'''\n" + (" "*iind)) + cnt[inxl+iind:],
                                     inxl, iind, rettype, "'''")
                braci = cnt.find("(", j)
                if braci != -1:
                    defi = cnt.find("def", j, braci)
                    if defi != -1:
                        propname = cnt[defi+3:braci].strip()
                        cci = 1
                        while (cci > 0) and braci < len(cnt):
                            braci += 1
                            if cnt[braci] == "(":
                                cci += 1
                            elif cnt[braci] == ")":
                                cci -= 1
                        icl = cnt.find(":", braci)
                        if icl != -1:
                            rrrettype = cnt[braci+1:icl].strip()
                            if rrrettype.startswith("->"):
                                rettype = rrrettype[2:].strip()
                                if rettype[0] in ['"', "'"]:
                                    rettype = rettype[1:-1]
                                inxl = cnt.find("\n", icl) + 1
                                if inxl != 0:
                                    iind = len(cnt[inxl:]) - len(cnt[inxl:].lstrip())
                                    sblk = cnt[inxl:].strip()[:3]
                                    for tblk in ["'''", '"""']:
                                        if sblk == tblk:
                                            cnt = moddocstr(propname, cnt, inxl, iind, rettype, sblk)
                                            break
                                    else:
                                        cnt = insdocstr(propname, cnt, inxl, iind, rettype)
                return cnt
            with open(ffp, "r") as f:
                cnt = f.read()
            j = None
            while True:
                j = cnt.rfind("@property", 0, j)
                if j == -1:
                    break
                cnt = patchprop(cnt, j)
            with open(ffp, "w") as f:
                f.write(cnt)
        pdirfs = annize.fs.Path(pdir)
        for ffp in pdirfs.rglob("/**/*.py"):
            if ffp.is_relative_to(pdirfs):
                patchfile(ffp)

    def __init__(self, *, show_undoc_members: bool = True, show_protected_members: bool = True):  # TODO exclude?!
        self.__show_undoc_members = show_undoc_members
        self.__show_protected_members = show_protected_members

    def generate_sources(self, rgeninfo):
        rgeninfo.configvalues["autodoc_default_options"] = {
            "member-order": "bysource",
        }
        #TODO ?!  with rgeninfo.source.path().temp_clone() as srcclone:
        srcclone = rgeninfo.source.path().temp_clone()
        self.__patch_property_types_in_docstrings(srcclone)
        env = dict(os.environb)
        apidocopts = ["members", "show-inheritance"]
        if self.__show_undoc_members:
            apidocopts += ["undoc-members"]
        env["SPHINX_APIDOC_OPTIONS"] = ",".join(apidocopts).encode()
        cmd = ["sphinx-apidoc", "--no-toc", "--implicit-namespaces", "--module-first"]
        if self.__show_protected_members:
            cmd += ["--private"]
        cmd += ["-o", rgeninfo.intstruct, srcclone]
        subprocess.check_call(cmd, env=env, cwd=srcclone)
        with open(f"{rgeninfo.intstruct}/index.rst", "w") as f:
            f.write(f"{annize.features.documentation.sphinx.rst.RstGenerator.heading(rgeninfo.heading)}\n"
                    f".. toctree::\n"
                    f"    :glob:\n"
                    f"\n"
                    f"    {srcclone.name}\n")
        return "index"
