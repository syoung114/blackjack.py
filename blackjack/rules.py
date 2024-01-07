import functools

from typing import List, Type
from enum import Enum

from blackjack import constants
from blackjack import cards

from blackjack.cards import Hand, Deck, Ordinal
from blackjack.exception.StupidProgrammerException import StupidProgrammerException

Split = List[Hand]

class PayoutOrd(Enum):
    ONE_ONE = 1,
    THREE_TWO = 2,
    TWO_ONE = 3

def payout(ord : PayoutOrd, bet : int) -> int:
    """
    Returns winnings relative to the bet. Representing losses is a matter of suffixing a negative to the result of this function, probably with input ONE_ONE.

    Complexity: O(1)
    """
    match ord:
        case PayoutOrd.ONE_ONE:
            return bet
        case PayoutOrd.THREE_TWO:
            return round(1.5 * bet)
        case PayoutOrd.TWO_ONE:
            return 2 * bet
        case _:
            raise StupidProgrammerException("Missing payout pattern match in blackjack.payout()")

def init_hand(deck : Deck) -> Hand:
    """
    Takes two cards from the deck, starting from the last key.

    Complexity: O(k) for size of initial hand

    Impure
    """
    h = []

    for _ in range(constants.INITIAL_HAND_LEN):
        cards.take_card(h, deck)

    return h

def compare(player : Hand, dealer : Hand, bet : int, win_odds : PayoutOrd=PayoutOrd.ONE_ONE) -> int:
    """
    Given two hands, modifies a bet depending on the value comparison.

    Complexity: O(n) for number of cards
    """
    player_bust = is_bust(player)
    dealer_bust = is_bust(dealer)

    if player_bust and dealer_bust:
        return bet

    elif player_bust and not dealer_bust:
        return 0

    elif not player_bust and dealer_bust:
        return bet + payout(win_odds, bet)

    result = cards.compare_hand(player, dealer)
    match result:
        case Ordinal.GT:
            return bet + payout(win_odds, bet)
        case Ordinal.EQ: # push
            return bet
        case Ordinal.LT:
            return 0
        case _:
            raise StupidProgrammerException("Missing pattern match in blackjack.compare()")


def winnings(hands : Split, dealer : Hand, bet : int) -> int:
    # naturals are 1:1 on split hands. fortunately this rule is accidentally built in already and nothing has to be done.
    return functools.reduce(
        lambda acc,hand: acc + compare(hand, dealer, bet),
        hands,
        0
    )

def is_natural(hand: Hand) -> bool:
    # this is an indirect check. it works. checking directly through the cards themselves is needlessly harder to do.
    return len(hand) == constants.INITIAL_HAND_LEN and is_max(hand)

def is_bust(hand : Hand) -> bool:
    return cards.hand_value(hand) > constants.MAX_HAND_VALUE

def is_max(hand : Hand) -> bool:
    return cards.hand_value(hand) == constants.MAX_HAND_VALUE

def can_split(hand : Hand) -> bool:
    return cards.card_rank_ord(hand[0]) == cards.card_rank_ord(hand[1])

def init_split(hand : Hand, deck : Deck) -> Split:
    return [[card, deck.pop()] for card in hand]

def is_insurable(hand : Hand) -> bool:
    # we can directly access the second card here but it's not shown to user. so this function pretends.
    return hand[0] == cards.Rank.ACE

def insurance_make_side_bet(bet) -> int:
    # TODO allow flexible adjusting depending on casino rules
    return round(bet / 2)

def insure(dealer : Hand, side_bet : int):
    if is_natural(dealer): # whereas a previous check might have observed just ace, this function observes entire hand
        return True, side_bet + payout(PayoutOrd.TWO_ONE, side_bet)
    else:
        return False, 0

def dealer_play(dealer : Hand, deck : Deck) -> Hand:
    while cards.hand_value(dealer) < constants.DEALER_STOP:
        cards.take_card(dealer, deck)

    return dealer
