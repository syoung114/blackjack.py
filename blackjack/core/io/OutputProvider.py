from abc import ABC, abstractmethod
from typing import Callable

from blackjack.core.state import GameState
from blackjack.core.cards import Hand

class OutputProvider(ABC):
    """
    Creates contextual side effects via a callback to a function like standard print().

    When implementing, please don't modify GameState. That will create bugs. Treat it as const.
    """
    ### This could be a hash map for potentially better performance but I think the features present in classes will become useful for future extension. The polymorphism alone is worth it.
    ### I also know that it's conceptually redundant to state that an abstract method is static but in Python it's required for overrides


# show methods -- text that shows without requiring further action
    
    @staticmethod
    @abstractmethod
    def show_player_hand(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_dealer_hand_down(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_dealer_hand_up(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_player_bust(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_dealer_bust(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_insurance_success(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_insurance_fail(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_bank(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_player_blackjack(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_max_hand(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    @abstractmethod
    def show_shuffling(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_keyboard_interrupt(state : GameState, writer : Callable[[str], None]):
        # it's safe to assume that this will be the standard library default (as below) or ""
        pass
