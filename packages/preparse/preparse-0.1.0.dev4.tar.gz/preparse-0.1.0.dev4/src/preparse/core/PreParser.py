import dataclasses
import os
import sys
import types
from typing import *

import click as cl
from datarepr import datarepr
from makeprop import makeprop
from tofunc import tofunc

from preparse._parsing.Parsing import *
from preparse.core.Click import *
from preparse.core.enums import *

__all__ = ["PreParser"]


@dataclasses.dataclass(kw_only=True)
class PreParser:
    __slots__ = (
        "_abbr",
        "_group",
        "_optdict",
        "_order",
        "_prog",
        "_warn",
    )

    def __init__(
        self: Self,
        optdict: Any = None,
        prog: Any = None,
        abbr: Any = Abbr.COMPLETE,
        group: Any = Group.MAINTAIN,
        order: Any = Order.PERMUTE,
        warn: Callable = str,
    ) -> None:
        "This magic method initializes self."
        self._optdict = dict()
        self.optdict = optdict
        self.prog = prog
        self.abbr = abbr
        self.group = group
        self.order = order
        self.warn = warn

    def __repr__(self: Self) -> str:
        "This magic method implements repr(self)."
        return datarepr(type(self).__name__, **self.todict())

    @makeprop()
    def abbr(self: Self, value: SupportsInt) -> Abbr:
        "This property decides how to handle abbreviations."
        return Abbr(value)

    def click(self: Self, cmd: Any = True, ctx: Any = True) -> Click:
        "This method returns a decorator that infuses the current instance into parse_args."
        return Click(parser=self, cmd=cmd, ctx=ctx)

    def copy(self: Self) -> Self:
        "This method returns a copy of the current instance."
        return type(self)(**self.todict())

    @makeprop()
    def group(self: Self, value: Any) -> dict:
        "This property decides how to approach the grouping of short options."
        return Group(value)

    @makeprop()
    def optdict(self: Self, value: Any) -> dict:
        "This property gives a dictionary of options."
        if value is None:
            self._optdict.clear()
            return self._optdict
        value = dict(value)
        value = {str(k): Nargs(v) for k, v in value.items()}
        self._optdict.clear()
        self._optdict.update(value)
        return self._optdict

    def parse_args(
        self: Self,
        args: Optional[Iterable] = None,
    ) -> list[str]:
        "This method parses args."
        if args is None:
            args = sys.argv[1:]
        return Parsing(
            parser=self.copy(),
            args=[str(a) for a in args],
        ).ans

    @makeprop()
    def order(self: Self, value: Any) -> Order:
        "This property decides how to order flags and positional arguments."
        if value == "infer_given":
            return Order.infer_given()
        if value == "infer_permute":
            return Order.infer_permute()
        return Order(value)

    @makeprop()
    def prog(self: Self, value: Any) -> str:
        "This property represents the name of the program."
        if value is None:
            value = os.path.basename(sys.argv[0])
        return str(value)

    def reflectClickCommand(self: Self, cmd: cl.Command) -> None:
        "This method causes the current instance to reflect a click.Command object."
        optdict = dict()
        for p in cmd.params:
            if not isinstance(p, cl.Option):
                continue
            if p.is_flag or p.nargs == 0:
                optn = Nargs.NO_ARGUMENT
            elif p.nargs == 1:
                optn = Nargs.REQUIRED_ARGUMENT
            else:
                optn = Nargs.OPTIONAL_ARGUMENT
            for o in p.opts:
                optdict[str(o)] = optn
        self.optdict.clear()
        self.optdict.update(optdict)

    def reflectClickContext(self: Self, ctx: cl.Context) -> None:
        "This method causes the current instance to reflect a click.Context object."
        self.prog = ctx.info_name

    def todict(self: Self) -> dict:
        "This method returns a dict representing the current instance."
        ans = dict()
        for slot in type(self).__slots__:
            name = slot.lstrip("_")
            ans[name] = getattr(self, slot)
        return ans

    @makeprop()
    def warn(self: Self, value: Callable) -> types.FunctionType:
        "This property gives a function that takes in the warnings."
        return tofunc(value)
