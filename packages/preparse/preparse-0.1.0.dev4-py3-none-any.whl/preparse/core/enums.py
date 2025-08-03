"""This module holds the enums for the project. \
Following the precedent of getopt, \
the value of two represents always an intermediary answer \
between the values zero, meaning no, and one, meaning yes."""

import enum
import os
from typing import *

__all__ = [
    "Abbr",
    "Group",
    "Order",
    "Nargs",
]


class BaseEnum(enum.IntEnum):
    @classmethod
    def _missing_(cls: type, value: Any) -> Self:
        return cls(2)


class Abbr(BaseEnum):
    REJECT = 0
    KEEP = 1
    COMPLETE = 2


class Group(BaseEnum):
    MINIMIZE = 0
    MAXIMIZE = 1
    MAINTAIN = 2


class Order(BaseEnum):
    GIVEN = 0
    POSIX = 1
    PERMUTE = 2

    @classmethod
    def _infer(cls: type) -> bool:
        return bool(os.environ.get("POSIXLY_CORRECT"))

    @classmethod
    def infer_given(cls: type) -> Self:
        return cls.POSIX if cls._infer() else cls.GIVEN

    @classmethod
    def infer_permute(cls: type) -> Self:
        return cls.POSIX if cls._infer() else cls.PERMUTE


class Nargs(BaseEnum):
    NO_ARGUMENT = 0
    REQUIRED_ARGUMENT = 1
    OPTIONAL_ARGUMENT = 2
