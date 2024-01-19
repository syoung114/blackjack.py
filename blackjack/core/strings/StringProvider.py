from abc import ABC, abstractmethod

from blackjack.core.state import GameState
from blackjack.core.cards import Hand

class StringProvider(ABC):
    """
    Strings for external IO, such as to user via stdin/stdout or for IPC

    When implementing, please don't create side effects with GameState. Treat it as const.
    """
    ### This could be a hash map for potentially better performance but I think the features present in classes will become useful for future extension. The polymorphism alone is worth it.
    ### I also know that it's conceptually redundant to state that an abstract method is static but in Python it's required for overrides

# ask methods -- these are prompts given when asking for input

    @staticmethod
    def ask_generic_fail(state : GameState):
        return ""

    @staticmethod
    @abstractmethod
    def ask_bank():
        # this function is an exception to requiring a GameState because at the time of asking about the bank, there is no state. It would be a catch 22.
        pass

    @staticmethod
    @abstractmethod
    def ask_bank_fail():
        pass

    @staticmethod
    @abstractmethod
    def ask_bet(state : GameState):
        pass

    @staticmethod
    def ask_bet_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

    @staticmethod
    @abstractmethod
    def ask_insurance(state : GameState):
        pass

    @staticmethod
    def ask_insurance_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

    @staticmethod
    @abstractmethod
    def ask_split(state : GameState):
        pass

    @staticmethod
    def ask_split_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

    @staticmethod
    @abstractmethod
    def ask_hit(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def ask_stay(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def ask_hit_stay_double(state : GameState):
        pass

    @staticmethod
    def ask_hit_stay_double_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

    @staticmethod
    @abstractmethod
    def ask_hit_stay(state : GameState):
        pass

    @staticmethod
    def ask_hit_stay_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

# input methods -- constrained texts that an input method must return

    @staticmethod
    @abstractmethod
    def input_yes():
        pass

    @staticmethod
    @abstractmethod
    def input_no():
        pass

    @staticmethod
    @abstractmethod
    def input_hit():
        pass

    @staticmethod
    @abstractmethod
    def input_stay():
        pass

    @staticmethod
    @abstractmethod
    def input_double():
        pass

# show methods -- text that shows without requiring further action
    
    @staticmethod
    @abstractmethod
    def show_player_hand(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_dealer_hand_down(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_dealer_hand_up(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_bust(hand : Hand):
        pass

    @staticmethod
    @abstractmethod
    def show_insurance_success(state : GameState):
        pass

    @staticmethod
    def show_insurance_fail(state : GameState):
        return StringProvider.ask_generic_fail(state)

    @staticmethod
    @abstractmethod
    def show_bank(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_player_blackjack(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_max_hand(state : GameState):
        pass

    @staticmethod
    @abstractmethod
    def show_shuffling(state : GameState):
        pass

    @staticmethod
    def show_keyboard_interrupt(state : GameState):
        # it's safe to assume that this will be the standard library default (as below) or ""
        return "KeyboardInterrupt"
