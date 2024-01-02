from . import StringProvider

class EnglishStrings(StringProvider):
    def __init__(self):
        pass 

    def hello(self) -> str:
        return "Hello"
