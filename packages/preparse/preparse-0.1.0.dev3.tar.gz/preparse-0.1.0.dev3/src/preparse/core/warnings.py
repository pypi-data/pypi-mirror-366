import abc
from typing import *

__all__ = [
    "PreparseAmbiguousOptionWarning",
    "PreparseInvalidOptionWarning",
    "PreparseRequiredArgumentWarning",
    "PreparseUnallowedArgumentWarning",
    "PreparseUnrecognizedOptionWarning",
    "PreparseWarning",
]


class PreparseWarning(Warning, metaclass=abc.ABCMeta):
    def __init__(self: Self, **kwargs: Any) -> None:
        "This magic method initializes the current instance."
        for n in type(self).__slots__:
            setattr(self, n, kwargs.pop(n))
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self: Self) -> str:
        "This magic method implements str(self)."
        return f"{self.prog}: {self.getmsg()}"

    @property
    def args(self: Self):
        "This property returns (str(self),)."
        return (str(self),)

    @abc.abstractmethod
    def getmsg(self: Self) -> str: ...


class PreparseAmbiguousOptionWarning(PreparseWarning):
    __slots__ = ("prog", "option", "possibilities")

    def getmsg(self: Self) -> str:
        "This method returns the core message."
        ans = "option %r is ambiguous; possibilities:" % self.option
        for x in self.possibilities:
            ans += " %r" % x
        return ans


class PreparseInvalidOptionWarning(PreparseWarning):
    __slots__ = ("prog", "option")

    def getmsg(self: Self) -> str:
        "This method returns the core message."
        return "invalid option -- %r" % self.option


class PreparseRequiredArgumentWarning(PreparseWarning):
    __slots__ = ("prog", "option")

    def getmsg(self: Self) -> str:
        "This method returns the core message."
        return "option requires an argument -- %r" % self.option


class PreparseUnallowedArgumentWarning(PreparseWarning):
    __slots__ = ("prog", "option")

    def getmsg(self: Self) -> str:
        "This method returns the core message."
        return "option %r doesn't allow an argument" % self.option


class PreparseUnrecognizedOptionWarning(PreparseWarning):
    __slots__ = ("prog", "option")

    def getmsg(self: Self) -> str:
        "This method returns the core message."
        return "unrecognized option %r" % self.option
