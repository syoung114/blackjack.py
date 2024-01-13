from enum import Enum
from typing import Callable, List
import queue

from blackjack import io

from tests.mocks_io import IOQueue, PrintMock, InputMock, print_stub

class InputRequireString(Enum):
    PROMPT = "prompt"
    FAIL = "fail"

def test_input_require_int():

    # main value we want
    ex = 42

    # queue mirroring the stdout we expect
    ex_output = queue.Queue()
    for s in [InputRequireString.PROMPT, InputRequireString.FAIL, InputRequireString.FAIL]:
        ex_output.put(s.value)

    print_mock = PrintMock()
    input_mock = InputMock(["abc", "", str(ex)])

    # do the thing. this will create side effects which the mocks will collect.
    result = io.input_require(
        int,
        InputRequireString.PROMPT.value,
        InputRequireString.FAIL.value,
        input_mock.input,
        print_mock.print
    )

    assert result == ex
    assert input_mock.empty()
    while not ex_output.empty():
        assert ex_output.get() == print_mock.get()

def test_input_require_int_within_invalid():

    class PredicateInterrupt(Exception):
        def __init__(self):
            super().__init__()
    
    class PrintWithCallback(IOQueue):
        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        def print(self, *args : List[str], end="\n") -> None:
            output = ' '.join(str(arg) for arg in args)
            self.put(output)
            self.callback()

    for i in [0, 98, 200, 1000]:
        constraint = io.Constraint().require(int).within(99, 199) # that range is arbitrary.

        input_mock = InputMock([str(i)])

        ex_output = queue.Queue()
        for item in [InputRequireString.PROMPT.value, InputRequireString.FAIL.value]:
            ex_output.put(item)

        def raise_pred():
            if input_mock.empty():
                raise PredicateInterrupt

        print_mock = PrintWithCallback(raise_pred) # we're not testing stdout but required to call the fn

        # do the thing. this will create side effects which the mocks will collect.
        try:
            io.input_require(
                constraint,
                InputRequireString.PROMPT.value,
                InputRequireString.FAIL.value,
                input_mock.input,
                print_mock.print
            )
        except PredicateInterrupt:
            pass

        assert input_mock.empty() # kind of redundant because the predicate above
        while not ex_output.empty():
            assert ex_output.get() == print_mock.get()

def test_input_require_int_within_valid():

    for ex in [99, 100, 150, 198, 199]:

        constraint = io.Constraint().require(int).within(99, 199) # that range is arbitrary.

        input_mock = InputMock([str(ex)])

        result = io.input_require(
            constraint,
            InputRequireString.PROMPT.value,
            InputRequireString.FAIL.value,
            input_mock.input,
            print_stub
        )
        assert result == ex

#def test_input_require_any_valid():
#    for 
    
