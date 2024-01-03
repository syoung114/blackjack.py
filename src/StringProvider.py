from abc import ABC, abstractmethod

from src.cards import Hand

class StringProvider(ABC):
    """
    Strings for external IO, such as to user via stdin/stdout or for IPC
    """
    ### This could be a hash map for potentially better performance but I prefer the polymorphism, immutibility, and strict interface.

# ask methods -- these are prompts given when asking for input

    @abstractmethod
    def ask_generic_fail(self) -> str:
        pass

    @abstractmethod
    def ask_bank(self) -> str:
        pass

    @abstractmethod
    def ask_bank_fail(self) -> str:
        return self.ask_generic_fail()

    @abstractmethod
    def initial_hand(self, player, dealer) -> str:
        pass

    @abstractmethod
    def ask_bet(self) -> str:
        pass

    def ask_bet_fail(self) -> str:
        return self.ask_generic_fail()

    @abstractmethod
    def ask_insurance(self) -> str:
        pass

    def ask_insurance_fail(self) -> str:
        return self.ask_generic_fail()

    @abstractmethod
    def ask_split(self) -> str:
        pass

    def ask_split_fail(self) -> str:
        return self.ask_generic_fail()

    @abstractmethod
    def ask_hit(self) -> str:
        pass

    @abstractmethod
    def ask_stay(self) -> str:
        pass

    @abstractmethod
    def ask_hit_stay(self) -> str:
        pass

    def ask_hit_stay_fail(self) -> str:
        return self.ask_generic_fail()

# input methods -- constrained texts that an input method must return

    @abstractmethod
    def input_yes(self) -> str:
        pass

    @abstractmethod
    def input_no(self) -> str:
        pass

    @abstractmethod
    def input_hit(self) -> str:
        pass

    @abstractmethod
    def input_stay(self) -> str:
        pass

# show methods -- text that shows without requiring further action

    @abstractmethod
    def show_insurance_success(self) -> str:
        pass

    @abstractmethod
    def show_insurance_fail(self) -> str:
        return self.ask_generic_fail()

    @abstractmethod
    def show_hand_status(self, hand : Hand) -> str:
        pass

    def show_keyboard_interrupt(self) -> str:
        # it's safe to assume that this will be the standard library default (as below) or ""
        return "KeyboardInterrupt"
