from functools import singledispatch
from .StringProvider import StringProvider

from blackjack.state import GameState, Hand
from blackjack.rules import hand_value

class StubStrings(StringProvider):
    """
    Not pretty but usable contextual strings.
    """

# ask methods -- these are prompts given when asking for input

    @staticmethod
    def ask_generic_fail(state : GameState):
        return "ask_generic_fail"

    @staticmethod
    def ask_bank():
        return "ask_bank"

    @staticmethod
    def ask_bank_fail():
        return "ask_bank_fail"

    @staticmethod
    def ask_bet(state : GameState):
        return "ask_bet"

    #@staticmethod
    #def ask_bet_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def ask_insurance(state : GameState):
        return "ask_insurance"

    #@staticmethod
    #def ask_insurance_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def ask_split(state : GameState):
        return "ask_split"

    #@staticmethod
    #def ask_split_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def ask_hit(state : GameState):
        return "ask_hit"

    @staticmethod
    def ask_stay(state : GameState):
        return "ask_stay"

    @staticmethod
    def ask_hit_stay(state : GameState):
        return "ask_hit_stay"

    #@staticmethod
    #def ask_hit_stay_fail(state : GameState):
    #    return .ask_generic_fail()

# input methods -- constrained texts that an input method must return

    @staticmethod
    def input_yes(state : GameState):
        return "yes"

    @staticmethod
    def input_no(state : GameState):
        return "no"

    @staticmethod
    def input_hit(state : GameState):
        return "hit"

    @staticmethod
    def input_stay(state : GameState):
        return "stay"

# show methods -- text that shows without requiring further action


    @staticmethod
    def show_player_hand(state_or_hand):
        @singledispatch
        def fn(hand : Hand):
            is_split = isinstance(hand, list)
            if is_split:
                return "\nplayer:".join(map(str, hand))
            else:
                return "player:" + str(hand)

        @fn.register(GameState)
        def _(state : GameState):
            return fn(state.player)

        return fn(state_or_hand)

    @staticmethod
    def show_dealer_hand_down(state : GameState):
        return "dealer:" + str(state.dealer[0])

    @staticmethod
    def show_dealer_hand_up(state : GameState):
        return "dealer:" + str(state.dealer)

    @staticmethod
    def show_bust(hand : Hand):
        return f"show_bust: {hand}"

    @staticmethod
    def show_insurance_success(state : GameState):
        return "show_insurance_success"

    #@staticmethod
    #def show_insurance_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def show_bank(state : GameState):
        return f"${state.bank}"

    @staticmethod
    def show_player_blackjack(state : GameState):
        return "blackjack"

    @staticmethod
    def show_max_hand(state : GameState):
        return "MAX HAND 21"

    @staticmethod
    def show_shuffling(state : GameState):
        return "SHUFFLING..."

    #@staticmethod
    #def show_keyboard_interrupt(state : GameState):
    #    # it's safe to assume that this will be the standard library default (as below) or ""
    #    return "KeyboardInterrupt"
