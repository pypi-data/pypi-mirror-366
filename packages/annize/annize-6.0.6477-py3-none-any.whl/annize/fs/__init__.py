# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Annize filesystem API.

Used by Annize Features.

See :py:class:`Path`, :py:class:`FilesystemContent` and others.
"""
import contextlib
import datetime
import os
import pathlib
import shutil
import typing as t

import annize.data
import annize.i18n


class FilesystemContent:
    """
    Base class for a source of arbitrary filesystem content.

    It provides access to that content by :py:meth:`path`. Some implementations will return a static path to already
    existing content, while other implementations will return a temporary path to ad-hoc generated content.

    This content can be a file, a complete directory, or anything else. It could even return a path that points to
    nothing. It depends on the actual implementation what kind of content it provides.

    This type is used instead of plain paths in situations where dynamic filesystem content might be exchanged (usually
    via some temporary files) instead of already existing files or directories. So, a :code:`FilesystemContent` usually
    provides a path for reading. There is no strict rule against writing at that path, but that might lead to expected
    behavior (e.g. when the path points to a temporary copy of something, so changes do not take the desired effect, or
    when it has undesired side effects on other consumers of the same instance). There might be features whose internal
    code does that in order to automatically handle relative paths.
    """

    def __init__(self, generate_func: t.Callable[[], "TInputPath"]):
        """
        :param generate_func: The content generator function. It has no parameters and returns an absolute path to the
                              content (usually inside some temporary directory).
        """
        self.__generate_func = generate_func
        self.__path = None

    def path(self) -> "Path":
        """
        Return the path that points to the content.

        It always returns the same path and does not do any further processing when called more than once (so it is safe
        and cheap to call that multiple times).
        """
        if self.__path is None:
            if not (path := Path(self.__generate_func())).is_absolute():
                raise ValueError(f"the `generate_func` must return an absolute path, not {path!r}")
            self.__path = path
        return self.__path


TInputPath = str|pathlib.Path
TFilesystemContent = TInputPath|FilesystemContent


class Path(pathlib.Path, FilesystemContent):
    """
    A path.

    This is compatible to :code:`pathlib.Path`, but provides some convenience methods that can safe a few lines of code
    for typical operations.

    Each path is also a :py:class:`FilesystemContent`. However, since :code:`FilesystemContent` only allows absolute
    paths, using a relative path as a :code:`FilesystemContent` will fail at runtime! See also :func:`content`.
    """

    def __init__(self, *args: TFilesystemContent):
        """
        :param args: Path parts. Often this is one string, one :code:`pathlib.Path` or one
                     :py:class:`FilesystemContent`. The latter one is only allowed as the first part.
        """
        pathlib.Path.__init__(self, "/".join([str(_.path()) if isinstance(_, FilesystemContent) else str(_)
                                              for _ in args]))
        FilesystemContent.__init__(self, lambda: self)

    def __call__(self, *args: TInputPath) -> "Path":
        """
        Return a path based on this one, but with the given parts appended.

        :param args: The part to append.
        """
        return Path(self, *args)

    def _path(self) -> "Path":
        """
        Return itself (in order to implement :py:class:`FilesystemContent`).
        """
        return self

    def path(self) -> "Path":
        """
        Return itself (in order to implement :py:class:`FilesystemContent`).
        """
        return self

    def children(self) -> t.Sequence["Path"]:
        """
        Like :code:`iterdir()`, but sorted by name.
        """
        return tuple(sorted(self.iterdir()))

    def ctime(self) -> datetime.datetime:
        """
        Return the ctime for this path.
        """
        return datetime.datetime.fromtimestamp(os.path.getctime(self))

    def mtime(self) -> datetime.datetime:
        """
        Return the mtime for this path.
        """
        return datetime.datetime.fromtimestamp(os.path.getmtime(self))

    def write_file(self, data: "bytes|annize.i18n.TrStrOrStr") -> None:
        """
        Write data to a file at this path (like :code:`write_text` or :code:`write_bytes`).

        :param data: The data to write.
        """
        if isinstance(data, annize.i18n.TrStr):
            data = str(data)
        if isinstance(data, str):
            self.write_text(data)
        else:
            self.write_bytes(data)

    def remove(self, *, missing_ok: bool = True) -> None:
        """
        Remove the file, directory, symlink, ... at this path.

        :param missing_ok: Whether it is okay if there is nothing at this path.
        """
        if self.is_dir(follow_symlinks=False):
            # renaming before removing makes it more robust (e.g. on windows)
            self.rename(new_path := self.parent(annize.data.UniqueId().long_str))
            shutil.rmtree(new_path)
        else:
            self.unlink(missing_ok=missing_ok)

    def file_size(self) -> int:
        """
        Return the file size in bytes.
        """
        return os.path.getsize(self)

    def temp_clone(self, *, temp_root_path: TInputPath|None = None, basename: str|None = None) -> "Path":
        """
        Return a temporary clone of the content at this path.

        :param temp_root_path: Optional root directory for temporary files. If unset, an OS-default will be used.
        :param basename: Optional new basename. If unset, the original one will be used.
        """
        ffresh_temp_directory = fresh_temp_directory(temp_root_path=temp_root_path)
        clone_destination = ffresh_temp_directory.path(basename or self.name)
        self.copy_to(clone_destination)
        return ffresh_temp_directory.path(clone_destination.name)

    TTransferFilter = t.Callable[["Path", "Path", "Path"], bool]  # relative path, source path, destination path

    def copy_to(self, destination: TInputPath, *, destination_as_parent: bool = False, merge: bool = False,
                overwrite: bool = False, transfer_filter: TTransferFilter|None = None) -> "Path":
        """
        Copy the file, directory, symlink, ... at this path to a given destination.
        All missing parent directories in the destination path get created automatically.

        :param destination: The destination.
        :param destination_as_parent: Whether to consider the destination as the parent of the new destination (instead
                                      of the new destination itself). The actual destination will have the same basename
                                      as the source then.
        :param merge: Whether to merge the source content into the destination. If not, each new destination directory
                      will replace the existing one or even fail.
        :param overwrite: Whether to allow overwriting of the destination.
        :param transfer_filter: The optional transfer filter to use. It can exclude particular parts from the transfer.
                                It is a function with three :py:class:`Path` parameters: The relative path of an item,
                                the absolute source path and the absolute destination path. It returns :code:`False` to
                                skip that item.
        """
        return Path._TransferHelper.transfer_to(self, Path(destination), merge=merge, overwrite=overwrite,
                                                destination_as_parent=destination_as_parent,
                                                action=Path._TransferHelper.transfer_action_copy,
                                                transfer_filter=transfer_filter)

    def move_to(self, destination: TInputPath, *, destination_as_parent: bool = False, merge: bool = False,
                overwrite: bool = False, transfer_filter: TTransferFilter|None = None) -> "Path":
        """
        Move the file, directory, symlink, ... at this path to a given destination.
        All missing parent directories in the destination path get created automatically.

        :param destination: The destination.
        :param destination_as_parent: Whether to consider the destination as the parent of the new destination (instead
                                      of the new destination itself). The actual destination will have the same basename
                                      as the source then.
        :param merge: Whether to merge the source content into the destination. If not, each new destination directory
                      will replace the existing one or even fail.
        :param overwrite: Whether to allow overwriting of the destination.
        :param transfer_filter: The optional transfer filter to use. It can exclude particular parts from the transfer.
                                It is a function with three :py:class:`Path` parameters: The relative path of an item,
                                the absolute source path and the absolute destination path. It returns :code:`False` to
                                skip that item.
        """
        return Path._TransferHelper.transfer_to(self, Path(destination), merge=merge, overwrite=overwrite,
                                                destination_as_parent=destination_as_parent,
                                                action=Path._TransferHelper.transfer_action_move,
                                                transfer_filter=transfer_filter)

    class TransferFilters:

        class And:

            def __init__(self, *inner_filters: "Path.TTransferFilter"):
                self.__inner_filters = inner_filters

            def __call__(self, relative_path: "Path", source: "Path", destination: "Path") -> bool:
                for inner_filter in self.__inner_filters:
                    if not inner_filter(relative_path, source, destination):
                        return False
                return True

    class _TransferHelper:

        @staticmethod
        def transfer_to(source: "Path", destination: "Path", *,
                        merge: bool, overwrite: bool, destination_as_parent: bool,
                        action: t.Callable, transfer_filter: "Path.TTransferFilter|None" = None) -> "Path":
            if destination_as_parent:
                return Path._TransferHelper.transfer_to(
                    source, destination(source.name), merge=merge, overwrite=overwrite, destination_as_parent=False,
                    action=action, transfer_filter=transfer_filter)
            destination.parent.mkdir(exist_ok=True, parents=True)
            Path._TransferHelper.__transfer_piece(action, transfer_filter, source, destination, merge, overwrite)
            return destination

        @staticmethod
        @contextlib.contextmanager
        def transfer_action_copy(source: "Path", destination: "Path") -> None:
            if source.is_symlink():
                os.symlink(os.readlink(source), destination)
                shutil.copystat(source, destination, follow_symlinks=False)
            elif source.is_dir():
                destination.mkdir(exist_ok=True)
                shutil.copystat(source, destination, follow_symlinks=False)
            elif source.is_file():
                shutil.copy2(source, destination)
            else:
                raise IOError(f"unknown kind {source!r}")
            yield

        @staticmethod
        @contextlib.contextmanager
        def transfer_action_move(source: "Path", destination: "Path") -> None:
            if source.is_symlink() or source.is_file():
                shutil.move(source, destination)
            elif source.is_dir():
                destination.mkdir(exist_ok=True)
                shutil.copystat(source, destination, follow_symlinks=False)
            else:
                raise IOError(f"unknown kind {source!r}")
            yield
            if source.is_dir():
                try:
                    os.rmdir(source)
                except IOError:
                    pass

        @staticmethod
        def __transfer_piece(action: t.Callable, transfer_filter: "Path.TTransferFilter|None",
                             source: "Path", destination: "Path", merge: bool, overwrite: bool,
                             relative_path: str = "") -> None:
            if transfer_filter and not transfer_filter(Path(relative_path), source, destination):
                return
            if destination.exists():
                if not (merge and source.is_dir() and destination.is_dir()):
                    if overwrite:
                        destination.remove()
                    else:
                        raise FileExistsError(f"already exists: {destination!r}")
            with action(source, destination):
                if source.is_dir():
                    for sourcechild in source.children():
                        destinationchild = destination(sourcechild.name)
                        Path._TransferHelper.__transfer_piece(
                            action, transfer_filter, sourcechild, destinationchild, merge, overwrite,
                            f"{relative_path}/{sourcechild.name}")


def content(f: TFilesystemContent, *, root: TFilesystemContent|None = None) -> FilesystemContent:
    """
    Return a :py:class:`FilesystemContent` for an arbitrary given path or :py:class:`FilesystemContent`.

    If the input already is a valid :py:class:`FilesystemContent`, it gets returned as-is. If the input is a string,
    it automatically gets interpreted as a path (like :py:class:`Path`). If it is a relative path, this function will
    return a :py:class:`FilesystemContent` that interprets it relative to the current Annize project root directory
    (which only makes sense when used inside an Annize project execution) or another root location.

    :param f: The input path or filesystem content.
    :param root: The path or filesystem content to be used as root directory for relative paths in :code:`f`.
    """
    if isinstance(f, str):
        f = Path(f)
    if isinstance(f, Path) and not f.is_absolute():
        import annize.features.files.common as _files
        f = _files.FsEntry(path=f, root=_files.ProjectDirectory() if root is None else content(root))
    return f


def fresh_temp_directory(name: TInputPath|None = None, *,
                         temp_root_path: TInputPath|None = None) -> "annize.fs.ext.FreshTempDirectory":
    """
    Return a fresh empty temporary directory for arbitrary usage.

    This directory will automatically be removed after the Annize project run has been finished.
    It can only be used for a :code:`with`-block, which removes it directly after this block.
    Each instance can only be used once in the latter way.

    For usage without a :code:`with`-block, see :py:attr:`annize.fs.ext.FreshTempDirectory.path`.

    :param name: The optional directory name. Otherwise, the implementation will choose a name.
    :param temp_root_path: Optional root directory for temporary files. If unset, an OS-default will be used.
    """
    return annize.fs.ext.FreshTempDirectory(name, temp_root_path=temp_root_path)


def dynamic_file(*, content: "annize.fs.ext.DynamicFile._TContent", file_name: str|None = None,
                 temp_root_path: TInputPath|None = None) -> FilesystemContent:
    """
    Return a 'filesystem content' that provides a file with some given content.

    :param content: The content of this dynamic file. This may be either direct content (:code:`str` or :code:`bytes`)
                    or a function that returns content.
    :param file_name: The optional file name. Otherwise, the implementation will choose a name.
    :param temp_root_path: Optional root directory for temporary files. If unset, an OS-default will be used.
    """
    return annize.fs.ext.DynamicFile(content=content, file_name=file_name, temp_root_path=temp_root_path)


import annize.fs.ext
