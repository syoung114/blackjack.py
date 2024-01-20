from abc import ABC, abstractmethod
from typing import Callable

from blackjack.core.state import GameState, PlayerAction

class InputProvider(ABC):

    @staticmethod
    @abstractmethod
    def input_bank(reader : Callable[..., str], writer : Callable[[str], None]) -> int:
        # this method doesn't ask for state because there's probably no state when this question is asked
        pass

    @staticmethod
    @abstractmethod
    def input_bet(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> int:
        pass

    @staticmethod
    @abstractmethod
    def input_hit(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> PlayerAction:
        pass

    @staticmethod
    @abstractmethod
    def input_hit_stay_double(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> PlayerAction:
        pass

    @staticmethod
    @abstractmethod
    def input_want_split(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def input_want_insurance(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> bool:
        pass
