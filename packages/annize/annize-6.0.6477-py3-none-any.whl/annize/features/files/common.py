# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Files and directories.
"""
import os
import re
import typing as t

import annize.features.base
import annize.fs


class FsEntry(annize.fs.FilesystemContent):
    """
    A filesystem location, either relative to the Annize project root directory or another root.

    If it is already known whether the entry is a file or a directory, consider using :py:class:`File` or
    :py:class:`Directory` instead. Special files (e.g. symlinks) can also be represented by a :py:class:`File`.
    """

    def __init__(self, *, path: annize.fs.TInputPath|None, root: annize.fs.TFilesystemContent|None):
        """
        :param path: The path that points to the referenced content (relative to :code:`root`).
        :param root: The root directory. If unset, it is the Annize project root directory.
        """
        super().__init__(self._path)
        self.__root = annize.fs.content(root or ProjectDirectory())
        self.__relative_path = annize.fs.Path(path or "")

    @property
    def root(self) -> annize.fs.FilesystemContent:
        """
        The root directory.

        :py:attr:`relative_path` is considered to be relative to this one.
        """
        return self.__root

    @property
    def relative_path(self) -> annize.fs.Path:
        """
        The path that points to the referenced content (relative to :py:attr:`root`).
        """
        return self.__relative_path

    def _path(self):
        return annize.fs.Path(self.__root, self.__relative_path)


class File(FsEntry):
    """
    A file location, either relative to the Annize project root directory or another root.
    """


class Exclude:
    """
    An exclusion definition. Usually used with :class:`Directory` and :class:`DirectoryPart`.
    """

    def __init__(self, *, by_path_pattern: str|None, by_path: str|None,
                 by_name_pattern: str|None, by_name: str|None):
        """
        :param by_path_pattern: Exclude by this regexp pattern on the full path.
        :param by_path: Exclude this path.
        :param by_name_pattern: Exclude by this regexp pattern on the file name.
        :param by_name: Exclude this file name.
        """
        self.__by_path_pattern = re.compile(by_path_pattern) if by_path_pattern else None
        self.__by_path = by_path
        self.__by_name_pattern = re.compile(by_name_pattern) if by_name_pattern else None
        self.__by_name = by_name

    @staticmethod
    def __does_exclude(text: str, by_text: str, by_pattern: re.Pattern) -> bool:
        return (by_text == text) or (by_pattern and by_pattern.fullmatch(text))

    def does_exclude(self, relative_path: annize.fs.Path, source: annize.fs.Path, destination: annize.fs.Path) -> bool:
        """
        Return whether a given location is excluded by this exclusion definition.

        :param relative_path: The relative path to check for exclusion.
        :param source: The absolute source path.
        :param destination: The absolute destination path.
        """
        return (self.__does_exclude(str(relative_path), self.__by_path, self.__by_path_pattern)
                or self.__does_exclude(relative_path.name, self.__by_name, self.__by_name_pattern))


class ExcludeAllBut(Exclude):
    """
    A negative exclusion definition.

    It will exclude an item whenever _none_ of the given inner exclude definitions match.
    """

    def __init__(self, *, excludes: list[Exclude]):
        """
        :param excludes: List of inner exclude definitions.
        """
        super().__init__(by_path_pattern=None, by_path=None, by_name_pattern=None, by_name=None)
        self.__excludes = excludes

    def does_exclude(self, relative_path, source, destination):
        for exclude in self.__excludes:
            if exclude.does_exclude(relative_path, source, destination):
                return False
        return True


class DirectoryPart:
    """
    A part of a directory. Used in :py:class:`Directory`.
    """

    def __init__(self, *, excludes: t.Iterable[Exclude], root: annize.fs.TFilesystemContent|None,
                 source_path: annize.fs.TInputPath|None = None, destination_path: annize.fs.TInputPath|None = None,
                 path: annize.fs.TInputPath|None = None, destination_is_parent: bool = False):
        """
        :param excludes: List of exclusion definitions.
        :param root: The root directory. If unset, it is the root directory specified for the owning
                     :py:class:`Directory`.
        :param source_path: The path that points to the referenced content (relative to :code:`root`).
        :param destination_path: The relative destination path inside the owning :py:class:`Directory`.
        :param path: Shorter way to set :code:`source_path` and :code:`destination_path` to the same path.
        :param destination_is_parent: Whether to consider the destination path as the parent of the new destination
                                      (instead of the new destination itself). The actual destination will have the same
                                      basename as the source then.
        """
        if path is not None:
            if (source_path is not None) or (destination_path is not None):
                raise ValueError("there can be no `source_path` or `destination_path` if `path` was given")
            source_path = destination_path = path
        self.__excludes = tuple(excludes or ())
        self.__root = None if root is None else annize.fs.content(root)
        self.__source_path = annize.fs.Path(source_path or "")
        self.__destination_path = annize.fs.Path(destination_path or "")
        self.__destination_is_parent = destination_is_parent

    @property
    def excludes(self) -> t.Sequence[Exclude]:
        """
        Exclusion definitions.
        """
        return self.__excludes

    @property
    def root(self) -> annize.fs.FilesystemContent|None:
        """
        The root directory (or :code:`None` for the owning :py:attr:`Directory.root`).

        :py:attr:`source_path` is considered to be relative to this one.
        """
        return self.__root

    @property
    def source_path(self) -> annize.fs.Path:
        """
        The path that points to the referenced content (relative to :py:attr:`root`).
        """
        return self.__source_path

    @property
    def destination_path(self) -> annize.fs.Path:
        """
        The relative destination path inside the owning :py:class:`Directory`.

        See also :py:attr:`destination_is_parent`.
        """
        return self.__destination_path

    @property
    def destination_is_parent(self) -> bool:
        """
        Whether to consider the destination path as the parent of the new destination (instead of the new destination
        itself).
        """
        return self.__destination_is_parent


class Directory(FsEntry):
    """
    A directory location, either relative to the Annize project root directory or another root.

    Depending on how it is configured, this might point to a dynamically generated temporary location (e.g. if it is
    composed of parts or excludes are specified).
    """

    def __init__(self, *, path: str|None, root: annize.fs.TFilesystemContent|None, excludes: t.Iterable[Exclude],
                 parts: t.Iterable[DirectoryPart], name: str|None):
        """
        :param path: The path that points to the referenced directory (relative to :code:`root`).
                     If set, do not set :code:`parts`!
        :param root: The root directory. If unset, it is the Annize project root directory.
        :param excludes: Exclusion specifications. If some are specified, this directory will be dynamically generated.
                         If set, do not set :code:`parts`!
        :param parts: Directory parts. If some are specified, this directory will be dynamically generated. Also, do not
                      set :code:`path` or :code:`excludes`!
        :param name: The name that this directory shall have (instead of its original name). If specified, this
                     directory will be dynamically generated. It must not contain directory separator characters (mostly
                     :code:`"/"`).
        """
        excludes = tuple(excludes)
        parts = tuple(parts)
        if parts:
            if path is not None:
                raise ValueError("it is not allowed to specify `path` and also `parts`")
            if excludes:
                raise ValueError("it is not allowed to specify `excludes` and also `parts`")
        if name and (os.sep in name or (os.altsep and os.altsep in name)):
            raise ValueError(f"name {name!r} contains forbidden characters")

        super().__init__(root=root, path=path)
        self.__excludes = tuple(excludes)
        self.__parts = tuple(parts)
        self.__name = name

    @property
    def parts(self) -> t.Sequence[DirectoryPart]:
        return self.__parts

    @property
    def excludes(self) -> t.Sequence[Exclude]:
        return self.__excludes

    def _path(self):
        root_path = annize.fs.Path(self.root)

        if not self.__parts and not self.__excludes and not self.__name:
            return root_path(self.relative_path)

        result = annize.fs.fresh_temp_directory(self.__name).path
        parts = list(self.__parts)

        if not parts:  # further processing is based on parts, but in some cases there are no parts
            parts.append(DirectoryPart(root=root_path, path=self.relative_path, excludes=self.__excludes))

        for part in parts:
            transfer_filter = annize.fs.Path.TransferFilters.And(*(self.__transfer_filter_for_exclude(exclude)
                                                                   for exclude in part.excludes))

            part_source = annize.fs.Path(part.root or root_path)
            if part.source_path:
                part_source = part_source(part.source_path)
            part_destination = result
            if part.destination_path:
                part_destination = part_destination(part.destination_path)

            part_source.copy_to(part_destination, merge=True, transfer_filter=transfer_filter,
                                destination_as_parent=part.destination_is_parent)

        return result

    @staticmethod
    def __transfer_filter_for_exclude(exclude: Exclude) -> "annize.fs.Path.TTransferFilter":
        def transfer_filter(relative_path, source, destination):
            return not exclude.does_exclude(relative_path, source, destination)
        return transfer_filter


class ProjectDirectory(annize.fs.FilesystemContent):
    """
    The Annize project root directory.
    """

    def __init__(self):
        super().__init__(self._path)

    def _path(self):
        return annize.features.base.project_directory()


class MachineRootDirectory(annize.fs.FilesystemContent):
    """
    The machine root directory, i.e. :code:`/`.
    """

    def __init__(self):
        super().__init__(self._path)

    def _path(self):
        return annize.fs.Path("/")
