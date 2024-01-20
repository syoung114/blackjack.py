"""
Relatively pure logic for external interaction, including with that of the reader or the system.

"""
from functools import partial
from typing import Any, Callable

class Constraint():
    def __init__(self, dtype: Any, pred=lambda _: True):
        # probably safer to fully encapsulate this instead of parameterizing it
        self._dtype = dtype
        self.pred = pred

    def __call__(self, x : Any) -> bool:
        # Example:
        # >>> constraint = Constraint[int]().within(1,9)
        # >>> constraint(5)
        # True
        # >>>
        return self.pred(x)

    def within(self, lower, upper):
        # note within() can also be `(at_least . at_most) x`
        return Constraint(
            self._dtype,
            self.pred and partial(
                lambda lower, upper, x: lower <= x <= upper,
                lower,
                upper
            )
        )

    def equalsAny(self, *vals):
        return Constraint(
            self._dtype,
            self.pred and partial(
                lambda vals,x: any(x==val for val in vals),
                vals
            )
        )

    def at_least(self, lower : int):
        return Constraint(
            dtype=self._dtype,
            pred=self.pred and partial(
                lambda lower,x: x >= lower,
                lower
            )
        )

def input_require(
    constraint : Constraint,
    prompt : str,
    fail_prompt : str,
    reader : Callable[..., str],
    output : Callable[[str], None],
):
    output(prompt)
    while True:
        response = reader()
        try:
            # if it meets the constraint
            try_cast = constraint._dtype(response)
            if constraint(try_cast):
                return try_cast
        except ValueError:
            pass
        except TypeError:
            pass
        output(fail_prompt)

def ask_binary(response_yes : str, response_no : str, prompt_normal : str, prompt_fail : str, reader : Callable[..., str], writer : Callable[[str], None]):
    constraint = Constraint(str).equalsAny(response_yes, response_no)
    do_hs = input_require(constraint, prompt_normal, prompt_fail, reader, writer)
    return do_hs == response_yes

