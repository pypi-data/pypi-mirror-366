# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
git-based version control.
"""
import datetime
import subprocess
import typing as t

import annize.features.base
import annize.features.files.common
import annize.features.version_control.common
import annize.fs


class VersionControlSystem(annize.features.version_control.common.VersionControlSystem):

    def __init__(self, *, path: str|None):
        super().__init__()
        self.__path = path or ""

    @property
    def path(self) -> annize.fs.Path:
        return annize.features.base.project_directory()(self.__path)

    def __call_git(self, cmdline: list[str]) -> str:
        return subprocess.check_output(["git", *cmdline], cwd=self.path).decode()  # TODO git path?! TODO noh utility paths?

    def get_current_revision(self):
        try:
            return self.__call_git(["log", "-1", "--pretty=format:%H"]).strip()
        except subprocess.CalledProcessError:
            # TODO was dann?
            return None

    def get_revision_list(self):
        try:
            ans = self.__call_git(["rev-list", "HEAD"])
            return list(reversed([line for line in [line.strip() for line in ans.split("\n")] if line]))
        except subprocess.CalledProcessError:
            # TODO was dann?
            return []

    def get_commit_message(self, revision):
        try:
            return self.__call_git(["log", revision, "-n1", "--format=format:%B"])
        except subprocess.CalledProcessError:
            # TODO was dann?
            return ""

    def get_commit_time(self, revision):
        try:
            return datetime.datetime.fromtimestamp(float(self.__call_git(["log", revision, "-n1",
                                                                          "--format=format:%ct"])))
        except subprocess.CalledProcessError:
            # TODO was dann?
            return None

    def get_revision_number(self, revision):
        for revisionbindex, revisionb in enumerate(self.get_revision_list()):
            if revisionb.startswith(revision):
                return revisionbindex + 1
        return None  # TODO


class ExcludeByGitIgnores(annize.features.files.common.Exclude):

    def __init__(self):
        super().__init__(by_path_pattern=None, by_path=None, by_name_pattern=None, by_name=None)

    def does_exclude(self, relative_path, source, destination):
        if source.name == ".git":  # TODO move to files.common.UsualExcludes ?!
            return True
        try:
            gitls = subprocess.check_output(["git", "ls-files", source.name], cwd=source.parent)
        except subprocess.CalledProcessError:
            return False
        return gitls.strip() == b""
