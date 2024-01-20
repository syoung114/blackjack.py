from functools import singledispatch
from typing import Callable

from blackjack.core.io.OutputProvider import OutputProvider
from blackjack.core.state import GameState, Hand
from blackjack.core.rules import hand_value

class BareOutput(OutputProvider):
    """
    Not pretty but usable contextual strings.
    """

# show methods -- text that shows without requiring further action

    @staticmethod
    def show_player_hand(state : GameState, writer : Callable[[str], None]):
        writer(f"player:{state.player[state.current_hand]}")

    @staticmethod
    def show_dealer_hand_down(state : GameState, writer : Callable[[str], None]):
        writer("dealer:" + str(state.dealer[0]))

    @staticmethod
    def show_dealer_hand_up(state : GameState, writer : Callable[[str], None]):
        writer("dealer:" + str(state.dealer))

    @staticmethod
    def show_player_bust(state : GameState, writer : Callable[[str], None]):
        writer(f"show_player_bust: {state.player[state.current_hand]}")

    @staticmethod
    def show_dealer_bust(state : GameState, writer : Callable[[str], None]):
        writer(f"show_bust: {state.dealer}")

    @staticmethod
    def show_insurance_success(state : GameState, writer : Callable[[str], None]):
        writer("show_insurance_success")

    @staticmethod
    def show_insurance_fail(state : GameState, writer : Callable[[str], None]):
        writer("show_insurance_fail")

    @staticmethod
    def show_bank(state : GameState, writer : Callable[[str], None]):
        writer(f"${state.bank}")

    @staticmethod
    def show_player_blackjack(state : GameState, writer : Callable[[str], None]):
        writer("blackjack")

    @staticmethod
    def show_max_hand(state : GameState, writer : Callable[[str], None]):
        writer("MAX HAND 21")

    @staticmethod
    def show_shuffling(state : GameState, writer : Callable[[str], None]):
        writer("SHUFFLING...")

    @staticmethod
    def show_keyboard_interrupt(state : GameState, writer : Callable[[str], None]):
        # there is an important check to make:
        # if state == None:
        # because state could be unbound. see implementation of driver.driver_io
        writer("KeyboardInterrupt")
