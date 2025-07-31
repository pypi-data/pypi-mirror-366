# Copyright 2023-2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""
Utilities related to the version of system.

.. versionadded:: 23.1.0
"""
from __future__ import annotations
import collections


__all__ = ["Version", "parse_version"]


class Version:
    """
    A representation of the version of a system.

    :param major: The major part of the version. Defaults to ``0``.
    :param minor: The minor part of the version. Defaults to ``0``.
    :param patch: The patch part of the version. Defaults to ``0``.

    It consists of three integer values for the ``major``, ``minor``, and ``patch`` parts of the
    version. The parts can be addressed through their name or index. It supports comparison to
    strings, sequences, mappings.

    Example:

    .. code-block:: python

        >>> v1 = Version(11, 22, 33)
        >>> assert v1.major == 11
        >>> assert v1[2] == 33
        >>> assert str(v1) == "11.22.33"
        >>> assert repr(v1) == "Version(major=11, minor=22, patch=33)"
        >>> v2 = Version(minor=44)
        >>> assert v2 == (0, 44)
        >>> assert [0, 44, 0] == v2
        >>> assert v2 == {"patch": 0, "minor": 44}

    .. note::

        Slices of the version are tuples. They are different from slices of the string
        representation of the same version.

        .. code-block:: python

            >>> v1 = Version(11, 22, 33)
            >>> assert v1[:2] == (11, 22)
            >>> assert str(v1)[:2] == "11"

    .. versionadded:: 23.1.0
    """

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        if not isinstance(major, int):
            raise TypeError(f"Argument 'major' must be an 'int', not '{type(major).__name__}'.")
        if not isinstance(minor, int):
            raise TypeError(f"Argument 'minor' must be an 'int', not '{type(minor).__name__}'.")
        if not isinstance(patch, int):
            raise TypeError(f"Argument 'patch' must be an 'int', not '{type(patch).__name__}'.")
        if major < 0:
            raise ValueError("Negative value for the 'major' part of the version.")
        if minor < 0:
            raise ValueError("Negative value for the 'minor' part of the version.")
        if patch < 0:
            raise ValueError("Negative value for the 'patch' part of the version.")
        self.__value = (major, minor, patch)

    @property
    def major(self) -> int:
        """The major part of the version."""
        return self.__value[0]

    @property
    def minor(self) -> int:
        """The minor part of the version."""
        return self.__value[1]

    @property
    def patch(self) -> int:
        """The patch part of the version."""
        return self.__value[2]

    def __str__(self) -> str:
        return ".".join([str(o) for o in self.__value])

    def __repr__(self) -> str:
        return "Version(major={}, minor={}, patch={})".format(*self.__value)

    def __getitem__(self, item):
        return self.__value[item]

    def __iter__(self):
        return iter(self.__value)

    def __cmp_helper(self, op: str, other: Version | str | tuple | list | dict) -> bool:
        """Generic comparison performing helper."""
        if isinstance(other, Version):
            o = other
        elif isinstance(other, str):
            o = parse_version(other)
        elif isinstance(other, collections.abc.Sequence):
            o = Version(*other)
        elif isinstance(other, collections.abc.Mapping):
            o = Version(**other)
        else:
            raise TypeError(
                f"Cannot compare a Version object to instances of '{type(other).__name__}'."
            )
        me = tuple(self)
        return getattr(me, op)(tuple(o))

    def __eq__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__eq__", other)

    def __ne__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__ne__", other)

    def __lt__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__lt__", other)

    def __le__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__le__", other)

    def __gt__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__gt__", other)

    def __ge__(self, other: Version | str | tuple | list | dict) -> bool:
        return self.__cmp_helper("__ge__", other)


def parse_version(value: str) -> Version:
    """
    Create a version object by parsing a string value.

    :param value: A version number.

        *   The version may have up to three parts.
        *   The version parts should be separated by periods (``.``).
        *   The version parts should be integers.

    :return: The parsed version.

    Example:

    .. code-block:: python

        >>> s = "11.22"
        >>> v = parse_version(s)
        >>> assert str(v) == "11.22.0"
        >>> assert repr(v) == "Version(major=11, minor=22, patch=0)"
        >>> assert v.major == 11
        >>> assert v[2] == 0

    .. versionadded:: 23.1.0
    """
    values = (int(o) for o in value.split("."))
    return Version(*values)
