from abc import ABC, abstractmethod

class StringProvider(ABC):
    @abstractmethod
    def hello() -> str:
        pass

    @abstractmethod
    def init_bank() -> str:
        pass

    @abstractmethod
    def generic_input_fail() -> str:
        pass

    @abstractmethod
    def initial_hand(player, dealer) -> str:
        pass

    @abstractmethod
    def ask_bet() -> str:
        pass
