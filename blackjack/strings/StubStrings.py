from .StringProvider import StringProvider

from blackjack.cards import Hand, hand_value

class StubStrings(StringProvider):
    """
    Strings for external IO, such as to user via stdin/stdout or for IPC
    """
    ### This could be a hash map for potentially better performance but I prefer the polymorphism, immutibility, and strict interface.

# ask methods -- these are prompts given when asking for input

    @staticmethod
    def ask_generic_fail() -> str:
        return "ask_generic_fail"

    @staticmethod
    def ask_bank() -> str:
        return "ask_bank"

    #@staticmethod
    #def ask_bank_fail() -> str:
    #    return .ask_generic_fail()

    @staticmethod
    def initial_hand(player, dealer) -> str:
        return f"Player:{StubStrings.show_hand_status(player)}\nDealer:{dealer[1]}"

    @staticmethod
    def ask_bet() -> str:
        return "ask_bet"

    #@staticmethod
    #def ask_bet_fail() -> str:
    #    return .ask_generic_fail()

    @staticmethod
    def ask_insurance() -> str:
        return "ask_insurance"

    #@staticmethod
    #def ask_insurance_fail() -> str:
    #    return .ask_generic_fail()

    @staticmethod
    def ask_split() -> str:
        return "ask_split"

    #@staticmethod
    #def ask_split_fail() -> str:
    #    return .ask_generic_fail()

    @staticmethod
    def ask_hit() -> str:
        return "ask_hit"

    @staticmethod
    def ask_stay() -> str:
        return "ask_stay"

    @staticmethod
    def ask_hit_stay() -> str:
        return "ask_hit_stay"

    #@staticmethod
    #def ask_hit_stay_fail() -> str:
    #    return .ask_generic_fail()

# input methods -- constrained texts that an input method must return

    @staticmethod
    def input_yes() -> str:
        return "yes"

    @staticmethod
    def input_no() -> str:
        return "no"

    @staticmethod
    def input_hit() -> str:
        return "hit"

    @staticmethod
    def input_stay() -> str:
        return "stay"

# show methods -- text that shows without requiring further action

    @staticmethod
    def show_insurance_success() -> str:
        return "show_insurance_success"

    #@staticmethod
    #def show_insurance_fail() -> str:
    #    return .ask_generic_fail()

    @staticmethod
    def show_hand_status(hand : Hand) -> str:
        return f"hand_status, val {hand_value(hand)} {hand}"

    @staticmethod
    def show_bust(hand: Hand) -> str:
        return f"show_bust: {hand}"

    @staticmethod
    def show_bank(bank : int) -> str:
        return f"${bank}"

    @staticmethod
    def show_blackjack() -> str:
        return "blackjack"

    @staticmethod
    def show_max_hand() -> str:
        return "MAX HAND 21"

    @staticmethod
    def show_shuffling() -> str:
        return "SHUFFLING..."

    #@staticmethod
    #def show_keyboard_interrupt() -> str:
    #    # it's safe to assume that this will be the standard library default (as below) or ""
    #    return "KeyboardInterrupt"
