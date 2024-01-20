from typing import Callable

from blackjack.core.io.OutputProvider import OutputProvider
from blackjack.core.state import GameState

class TestOutput(OutputProvider):
    """
    Provides the output interface without any effects.
    """

    @staticmethod
    def show_player_hand(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_dealer_hand_down(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_dealer_hand_up(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_player_bust(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_dealer_bust(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_insurance_success(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_insurance_fail(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_bank(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_player_blackjack(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_max_hand(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_shuffling(state : GameState, writer : Callable[[str], None]):
        pass

    @staticmethod
    def show_keyboard_interrupt(state : GameState, writer : Callable[[str], None]):
        pass
