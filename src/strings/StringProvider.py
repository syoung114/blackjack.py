from abc import ABC, abstractmethod

from src.cards import Hand

class StringProvider(ABC):
    """
    Strings for external IO, such as to user via stdin/stdout or for IPC
    """
    ### This could be a hash map for potentially better performance but I prefer the polymorphism, immutibility, and strict interface.
    ### I know that it's conceptually redundant to state that an abstract method is static but in Python it's required for overrides

# ask methods -- these are prompts given when asking for input

    @staticmethod
    def ask_generic_fail() -> str:
        pass

    @staticmethod
    @abstractmethod
    def ask_bank() -> str:
        pass

    def ask_bank_fail(self) -> str:
        return self.ask_generic_fail()

    @staticmethod
    @abstractmethod
    def initial_hand(player, dealer) -> str:
        pass

    @staticmethod
    @abstractmethod
    def ask_bet() -> str:
        pass

    def ask_bet_fail(self) -> str:
        return self.ask_generic_fail()

    @staticmethod
    @abstractmethod
    def ask_insurance() -> str:
        pass

    def ask_insurance_fail(self) -> str:
        return self.ask_generic_fail()

    @staticmethod
    @abstractmethod
    def ask_split() -> str:
        pass

    def ask_split_fail(self) -> str:
        return self.ask_generic_fail()

    @staticmethod
    @abstractmethod
    def ask_hit() -> str:
        pass

    @staticmethod
    @abstractmethod
    def ask_stay() -> str:
        pass

    @staticmethod
    @abstractmethod
    def ask_hit_stay() -> str:
        pass

    def ask_hit_stay_fail(self) -> str:
        return self.ask_generic_fail()

# input methods -- constrained texts that an input method must return

    @staticmethod
    @abstractmethod
    def input_yes() -> str:
        pass

    @staticmethod
    @abstractmethod
    def input_no() -> str:
        pass

    @staticmethod
    @abstractmethod
    def input_hit() -> str:
        pass

    @staticmethod
    @abstractmethod
    def input_stay() -> str:
        pass

# show methods -- text that shows without requiring further action

    @staticmethod
    @abstractmethod
    def show_insurance_success() -> str:
        pass

    def show_insurance_fail(self) -> str:
        return self.ask_generic_fail()

    @staticmethod
    @abstractmethod
    def show_hand_status(hand : Hand) -> str:
        pass

    def show_keyboard_interrupt(self) -> str:
        # it's safe to assume that this will be the standard library default (as below) or ""
        return "KeyboardInterrupt"
