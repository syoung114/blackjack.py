from functools import singledispatch
from typing import List
from enum import Enum

from src import constants
from src import cards

from src.cards import Hand, Deck, Ordinal
from src.exception.StupidProgrammerException import StupidProgrammerException

type Split = List[Hand]

class PayoutOrd(Enum):
    ONE_ONE = 1,
    THREE_TWO = 2,
    TWO_ONE = 3,
    PUSH = 4

def payout(ord : PayoutOrd, bet : int) -> int:
    """
    Returns winnings relative to the bet. Representing losses is a matter of suffixing a negative to the result of this function, probably with input ONE_ONE.

    Complexity: O(1)
    """
    match ord: # it took 30 years of python development to implement a switch...
        case PayoutOrd.ONE_ONE: # I know this is redundant but it's for consistency and maintainability. Since this is python we don't care about minimising CPU cycles anyway.
            return bet
        case PayoutOrd.THREE_TWO:
            return round(1.5 * bet)
        case PayoutOrd.TWO_ONE:
            return 2 * bet
        case PayoutOrd.PUSH:
            return 0
        case _:
            raise StupidProgrammerException("Missing payout pattern match in blackjack.payout()")

def init_hand(deck : Deck) -> Hand:
    """
    Takes two cards from the deck, starting from the last key.

    Complexity: O(1)

    Impure
    """
    h = []

    for _ in range(constants.INITIAL_HAND_LEN):
        cards.take_card(h, deck)

    return h

def compare(player : Hand, dealer : Hand, bet : int, payout_ord : PayoutOrd=PayoutOrd.ONE_ONE) -> int:
    """
    Given two hands, modifies a bet depending on the value comparison.
    """
    if is_bust(player) and is_bust(dealer):
        # same as Ordinal.EQ
        return payout(PayoutOrd.PUSH, bet)

    result = cards.compare_hand(player, dealer)
    match result:
        case Ordinal.GT:
            return payout(payout_ord, bet)
        case Ordinal.EQ:
            return payout(PayoutOrd.PUSH, bet)
        case Ordinal.LT:
            return -payout(payout_ord, bet)
        case _:
            raise StupidProgrammerException("Missing pattern match in blackjack.compare()")

def is_bust(hand : Hand) -> bool:
    return cards.hand_value(hand) > constants.MAX_HAND_VALUE

def is_max(hand : Hand) -> bool:
    return cards.hand_value(hand) == constants.MAX_HAND_VALUE

def is_valid_value(hand : Hand) -> bool:
    return cards.hand_value(hand) < constants.MAX_HAND_VALUE

def can_split(hand : Hand) -> bool:
    return cards.card_rank_ord(hand[0]) == cards.card_rank_ord(hand[1])

def init_split(hand : Hand) -> Split:
    return [[card] for card in hand]

def is_natural(hand: Hand) -> bool:
    return len(hand) == constants.INITIAL_HAND_LEN and is_max(hand)

def is_insurable(hand : Hand) -> bool:
    return hand[0] == cards.Rank.ACE

def insurance_make_side_bet(bet) -> int:
    # TODO allow flexible adjusting depending on casino rules
    return round(bet / 2)

def insure(dealer : Hand, side_bet : int):
    if is_natural(dealer): # whereas a previous check might have observed just ace, this function observes entire hand
        return True, payout(PayoutOrd.ONE_ONE, side_bet)
    else:
        return False, -payout(PayoutOrd.ONE_ONE, side_bet)

def dealer_play(dealer : Hand, deck : Deck) -> Hand:
    while cards.hand_value(dealer) < constants.DEALER_STOP:
        cards.take_card(dealer, deck)

    return dealer
