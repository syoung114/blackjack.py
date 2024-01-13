from blackjack.strings.StringProvider import StringProvider
from blackjack.state import GameState, Hand

class TestStrings(StringProvider):
    """
    Empty strings for when printing is irrelevant, like testing.
    """

# ask methods -- these are prompts given when asking for input

    @staticmethod
    def ask_generic_fail(state : GameState):
        return ""

    @staticmethod
    def ask_bank():
        return ""

    @staticmethod
    def ask_bank_fail():
        return ""

    @staticmethod
    def ask_bet(state : GameState):
        return ""

    #@staticmethod
    #def ask_bet_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def ask_insurance(state : GameState):
        return ""

    @staticmethod
    def show_insurance_fail(state : GameState):
        return ""

    @staticmethod
    def ask_split(state : GameState):
        return ""

    #@staticmethod
    #def ask_split_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def ask_hit(state : GameState):
        return ""

    @staticmethod
    def ask_stay(state : GameState):
        return ""

    @staticmethod
    def ask_hit_stay(state : GameState):
        return ""

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
        return ""

    @staticmethod
    def show_dealer_hand_down(state : GameState):
        return ""

    @staticmethod
    def show_dealer_hand_up(state : GameState):
        return ""

    @staticmethod
    def show_bust(hand : Hand):
        return ""

    @staticmethod
    def show_insurance_success(state : GameState):
        return ""

    #@staticmethod
    #def show_insurance_fail(state : GameState):
    #    return .ask_generic_fail()

    @staticmethod
    def show_bank(state : GameState):
        return ""

    @staticmethod
    def show_player_blackjack(state : GameState):
        return ""

    @staticmethod
    def show_max_hand(state : GameState):
        return ""

    @staticmethod
    def show_shuffling(state : GameState):
        return ""

    #@staticmethod
    #def show_keyboard_interrupt(state : GameState):
    #    # it's safe to assume that this will be the standard library default (as below) or ""
    #    return ""