import queue

from typing import List

class IOQueue:
    def __init__(self):
        self._q = queue.Queue()
        self._length = 0

    def empty(self) -> bool:
        return self._q.empty()

    def get(self):
        if not self.empty():
            return self._q.get()
        raise Exception("IOQueue.get() while queue empty()")

    def put(self, x):
        self._q.put(x)
        self._length += 1

    def length(self) -> int:
        return self._length

class PrintMock(IOQueue):
    def __init__(self):
        super().__init__()

    def print(self, *args : List[str], end="\n") -> None:
        output = ' '.join(str(arg) for arg in args)
        self.put(output)

class InputMock(IOQueue):
    def __init__(self, inputs : List[str]):
        super().__init__()
        for item in inputs:
            self.put(item)

    def input(self, prompt : str="") -> str:
        if not self.empty():
            return self.get()
        raise Exception("InputMock.Queue.get() while Queue.empty()")


def print_stub(*args : List[str], end="\n") -> None:
    pass
