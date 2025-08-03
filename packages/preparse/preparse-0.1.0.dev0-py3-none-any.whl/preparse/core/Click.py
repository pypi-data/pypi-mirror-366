import dataclasses
import functools
import types
from typing import *

__all__ = ["Click"]


@dataclasses.dataclass
class Click:

    parser: Any
    cmd: Any = True
    ctx: Any = True

    @functools.singledispatchmethod
    def __call__(self, target: Any) -> Any:
        "This magic method implements self(target)."
        target.parse_args = self(target.parse_args)
        return target

    @__call__.register
    def _(self, target: types.FunctionType) -> types.FunctionType:
        @functools.wraps(target)
        def ans(cmd, ctx, args):
            p = self.parser.copy()
            if self.cmd:
                p.reflectClickCommand(cmd)
            if self.ctx:
                p.reflectClickContext(ctx)
            return target(cmd, ctx, p.parse_args(args))

        return ans

    @__call__.register
    def _(self, target: types.MethodType) -> types.MethodType:
        func = self(target.__func__)
        ans = types.MethodType(func, target.__self__)
        return ans
