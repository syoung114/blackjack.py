"""
Relatively pure logic for external interaction, including with that of the reader or the system.

"""

from typing import Callable, Any
from functools import singledispatch

class Constraint():
    def __init__(self, dtype=str, pred=lambda: True):
        self.dtype = dtype
        self.pred = pred

    def require(self, dtype):
        return Constraint(dtype, self.pred)

    def within(self, lower, upper):
        return Constraint(
            self.dtype,
            lambda x: self.pred(x) and lower <= x <= upper
        )

    def equalsOr(self, *vals):
        return Constraint(
            self.dtype,
            lambda x: self.pred(x) and any(x==val for val in vals)
        )

    def equalsOrDiscrete(self, start, end):
        return Constraint(
            lambda x: self.pred(x) and any(x==i for i in range(start, end))
        )

@singledispatch
def input_require(
    constraint,
    prompt : str,
    fail_prompt : str,
    reader : Callable[..., str],
    output : Callable[[str], None]
):
    output(prompt)
    while True:
        usr = reader()
        try:
            result = constraint.dtype(usr)
            if constraint.pred(result):
                return result
        except ValueError:
            output(fail_prompt)

@input_require.register(Any)
def _(
    dtype,
    prompt : str,
    fail_prompt : str,
    reader : Callable[..., str],
    output : Callable[[str], None]
):
    return input_require(
        Constraint(dtype),
        prompt,
        fail_prompt,
        reader,
        output
    )
