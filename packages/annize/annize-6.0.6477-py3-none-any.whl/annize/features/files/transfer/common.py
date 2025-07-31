# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File transfers.
"""
import abc
import contextlib
import shlex
import tarfile
import typing as t

import annize.data
import annize.fs


class Endpoint(abc.ABC):

    @abc.abstractmethod
    def access_filesystem(self, rootpath: str) -> t.ContextManager[annize.fs.Path]:
        pass


class FsEndpoint(Endpoint):

    def __init__(self, *, fsentry: annize.fs.Path|None, path: str|None):#TODO path ?! (make annize.object.parameter_info autoconvert a str to FsEntry)
        super().__init__()
        self.__fs = annize.fs.Path(fsentry or path)  # TODO yy  or annize.fs.get_entry(path)

    @contextlib.contextmanager
    def access_filesystem(self, rootpath: str):
        yield self.__fs(rootpath)


class Upload:

    def __init__(self, *, source: annize.fs.FilesystemContent, destination_endpoint: Endpoint, destination_path: annize.fs.TInputPath|None):
        self.__source = source
        self.__destination_endpoint = destination_endpoint
        self.__destination_path = "/" + (destination_path or "").lstrip("/")#TODO dedup

    def __call__(self) -> None:
        """
        TODO
        umask = os.umask(0)
        os.umask(umask)
        def _chmod(_p):
            for x in os.listdir(_p):
                px = _p+"/"+x
                os.chmod(px, (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) & ~umask)
                if os.path.isdir(px):
                    _chmod(px)
        _chmod(hp.path)
        sshtgt = f"{self.__connection.username}@{self.__connection.host}:{self.__destination_path}"
        """
        fsource = self.__source.path()
        fdestination = annize.fs.Path(self.__destination_path, fsource.name)
        if getattr(self.__destination_endpoint, "has_shell_access", False):
            self.__destination_endpoint.exec(f"mkdir -p {shlex.quote(self.__destination_path)}")
            with annize.fs.fresh_temp_directory() as temp_dir:
                xfertarfs = temp_dir.path()("x.tgz")
                with tarfile.open(xfertarfs, "w:gz") as tar:
                    tar.add(fsource, arcname=fsource.name)
                with self.__destination_endpoint.access_filesystem(self.__destination_path) as destfs:
                    xfertarfsdest = destfs(f"{annize.data.UniqueId().long_str}.tgz")
                    xfertarfs.move_to(xfertarfsdest)
            self.__destination_endpoint.exec(f"rm -rf {shlex.quote(str(fdestination.path()))};"
                                             f"cd {shlex.quote(self.__destination_path)};"
                                             f"tar xfz {shlex.quote(xfertarfsdest.name)};"
                                             f"rm {shlex.quote(xfertarfsdest.name)}")
        else:
            with self.__destination_endpoint.access_filesystem(self.__destination_path) as destfs:
                fsource.copy_to(destfs(fsource.name), overwrite=True)
