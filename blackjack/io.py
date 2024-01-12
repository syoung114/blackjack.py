"""
Relatively pure logic for external interaction, including with that of the reader or the system.

"""

from typing import Callable
from functools import partial, singledispatch

class Constraint():
    def __init__(self, dtype=str, pred=lambda: True):
        self.dtype = dtype
        self.pred = pred

    def require(self, dtype):
        return Constraint(dtype, self.pred)

    def within(self, lower, upper):
        return Constraint(
            self.dtype,
            self.pred and partial(
                lambda lower, upper, x: lower <= x <= upper,
                lower,
                upper
            )
        )

    def equalsAny(self, *vals):
        return Constraint(
            self.dtype,
            self.pred and partial(
                lambda vals,x: any(x==val for val in vals),
                vals
            )
        )

@singledispatch
def input_require(
    dtype,
    prompt : str,
    fail_prompt : str,
    reader : Callable[..., str],
    output : Callable[[str], None],
    pred=lambda x: True
):
    output(prompt)
    while True:
        usr = reader()
        try:
            result = dtype(usr)
            if pred(result):
                return result
        except ValueError:
            pass
        output(fail_prompt)

@input_require.register(Constraint)
def _(
    constraint,
    prompt : str,
    fail_prompt : str,
    reader : Callable[..., str],
    output : Callable[[str], None]
):
    return input_require(
        constraint.dtype,
        prompt,
        fail_prompt,
        reader,
        output,
        pred=constraint.pred
    )

def ask_binary(input_yes : str, input_no : str, show_normal : str, show_fail : str, reader : Callable[..., str], writer : Callable[[str], None]):
    constraint = Constraint().equalsAny(input_yes, input_no)
    do_hs = input_require(constraint, show_normal, show_fail, reader, writer)
    return do_hs == input_yes

