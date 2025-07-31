# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize filesystem API extensions.

Note: Commonly used functionality is also available in simpler ways (e.g. somehow in :py:mod:`annize.fs`).
"""
import atexit
import subprocess
import tempfile
import time
import typing as t

import annize.data
import annize.fs as _fs


class FreshTempDirectory:
    """
    A fresh empty temp directory for arbitrary usage.

    See :py:func:`annize.fs.fresh_temp_directory`.
    """

    def __init__(self, name: _fs.TInputPath|None = None, *, temp_root_path: _fs.TInputPath|None = None):
        """
        Do not use directly.
        """
        super().__init__()
        temp_root_path = _fs.Path(temp_root_path or tempfile.gettempdir()).absolute()
        self.__outer_path = temp_root_path / str(annize.data.UniqueId())
        self.__path = self.__outer_path(name or "_")
        self.__path.mkdir(parents=True)
        atexit.register(self.__cleanup)  # TODO better?!

    def __enter__(self) -> _fs.Path:
        return self.__path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cleanup()

    @property
    def path(self) -> _fs.Path:
        """
        The path of this temp directory.

        It is empty after creation and will be removed automatically after usage.
        """
        return self.__path

    def __cleanup(self):
        try:
            self.__outer_path.remove()
        except IOError:
            pass


class DynamicFile(_fs.FilesystemContent):
    """
    A filesystem content that provides a file with some given content.

    See :py:func:`annize.fs.dynamic_file`.
    """

    _TStaticContent = str|bytes
    _TContent = _TStaticContent|t.Callable[[], _TStaticContent]

    def __init__(self, *, content: _TContent, file_name: str|None = None, temp_root_path: _fs.TInputPath|None = None):
        """
        Do not use directly.
        """
        super().__init__(self._path)
        self.__content = content
        self.__file_name = file_name or "_"
        self.__temp_root_path = temp_root_path

    def _path(self):
        result = FreshTempDirectory(temp_root_path=self.__temp_root_path)
        content = self.__content or b""
        if callable(content):
            content = content()
        if isinstance(content, str):
            content = content.encode()
        content_file = result.path(self.__file_name)
        with open(content_file, "wb") as f:
            f.write(content)
        return content_file


class Mount:
    """
    Mounting of a filesystem.

    This mounts a filesystem as long as its context is entered (:code:`with`-block).
    """

    def __init__(self, src: _fs.TInputPath, dst: _fs.TInputPath, *, options: t.Iterable[str] = (),
                 mount_command: t.Sequence[str] = ("mount",), umount_command: t.Sequence[str] = ("umount",)):
        """
        :param src: The filesystem to mount. Often a device file.
        :param dst: The mount-point.
        :param options: Additional mount options.
        :param mount_command: The mount command to use.
        :param umount_command: The umount command to use.
        """
        self.__src = _fs.Path(src)
        self.__destination = _fs.Path(dst)
        self.__options = options or []
        self.__mount_command = tuple(mount_command)
        self.__umount_command = tuple(umount_command)

    @property
    def destination(self) -> _fs.Path:
        """
        The mount-point.
        """
        return self.__destination

    def __enter__(self):
        subprocess.check_call([*self.__mount_command, self.__src, self.__destination, *self.__options])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in reversed(range(4)):
            subprocess.call(["sync"])
            try:
                subprocess.check_call([*self.__umount_command, self.__destination])
                break
            except subprocess.CalledProcessError:
                if i == 0:
                    raise
            time.sleep(1)
        else:
            raise Exception("TODO")
