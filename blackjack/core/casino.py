from math import floor
from abc import ABC, abstractmethod

from blackjack.core.PayoutOdds import PayoutOdds
from blackjack.core.exception.StupidProgrammerException import StupidProgrammerException

class HouseRules(ABC):
    @staticmethod
    @abstractmethod
    def win_payout(odds : PayoutOdds, bet : int) -> int:
        pass

    # TODO implement

    #@staticmethod
    #@abstractmethod
    #def allow_surrender() -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def allow_double() -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def allow_insurance() -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def allow_double_after_split() -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def allow_recursive_split() -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def num_decks() -> int:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def shuffle_pred(state, *args) -> bool:
    #    pass

    #@staticmethod
    #@abstractmethod
    #def allow_dealer_hit_soft_17() -> bool:
    #    pass

    
class TraditionalRules(HouseRules):
    @staticmethod
    def win_payout(odds : PayoutOdds, bet : int) -> int:
        """
        Returns positive winnings relative to the bet, according to the win_payout.
    
        Complexity: O(1)
        """
        if bet < 0:
            # this is a defensive measure to prevent a pre-exsting bug from spiraling into something worse
            raise ValueError(f"negative bet in rules.win_payout(): {bet}")
    
        match odds:
            case PayoutOdds.ONE_ONE:
                return bet
            case PayoutOdds.THREE_TWO:
                return floor(1.5 * bet) # them casinos wouldn't generously let you round up!
            case PayoutOdds.TWO_ONE:
                return 2 * bet
            case _:
                raise StupidProgrammerException("Missing win_payout pattern match in blackjack.win_payout()")

    #@staticmethod
    #def allow_surrender() -> bool:
    #    return False

