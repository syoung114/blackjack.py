import functools

from typing import List
from enum import Enum
from math import floor

from blackjack import constants
from blackjack import cards

from blackjack.cards import Hand, Deck, Rank
from blackjack.exception.StupidProgrammerException import StupidProgrammerException

Split = List[Hand]

class Ordinal(Enum):
    LT = -1
    EQ = 0
    GT = 1

class PayoutOrd(Enum):
    ONE_ONE = 1,
    THREE_TWO = 2,
    TWO_ONE = 3

def init_hand(deck : Deck) -> Hand:
    """
    Takes two cards from the deck, starting from the last key.

    Complexity: O(k) for size of initial hand

    Impure
    """
    ### the reason this is in rules and not cards is that the size of the hand is dependent on blackjack rules.
    h = []

    for _ in range(constants.INITIAL_HAND_LEN):
        cards.take_card(h, deck)

    return h

def hand_value(hand : Hand) -> int:
    """
    Accumulates the cards in a hand, including ace rules.

    Complexity: O(n)
    """
    # could refactor into functools.reduce/sum() but it might be less understandable.
    acc = 0
    aces_count = 0

    for card in hand:
        if card[0] == Rank.ACE:
            aces_count += 1
        else:
            acc += cards.card_value(card)

    # count aces...
    for _ in range(aces_count):
        if acc + Rank.ACE.value[1] <= constants.MAX_HAND_VALUE:
            acc += Rank.ACE.value[1]
        else:
            acc += Rank.ACE.value[0]

    return acc

def compare(a, b) -> Ordinal:
    """
    Returns GT,LT, or EQ for any number.

    Complexity: O(1)
    """
    if a > b:
        return Ordinal.GT
    elif a < b:
        return Ordinal.LT
    else:
        return Ordinal.EQ

def compare_hand(left_hand : Hand, right_hand : Hand) -> Ordinal:
    """
    Indicates which hand has the greater cumulative hand value.

    Complexity: O(n)
    """
    return compare(
        hand_value(left_hand),
        hand_value(right_hand)
    )

def payout(ord : PayoutOrd, bet : int) -> int:
    """
    Returns positive winnings relative to the bet, according to the payout.

    Complexity: O(1)
    """
    if bet < 0:
        # this is a defensive measure to prevent a pre-exsting bug from spiraling into something worse
        raise ValueError(f"negative bet in rules.payout(): {bet}")

    match ord:
        case PayoutOrd.ONE_ONE:
            return bet
        case PayoutOrd.THREE_TWO:
            return floor(1.5 * bet) # them casinos wouldn't generously let you round up!
        case PayoutOrd.TWO_ONE:
            return 2 * bet
        case _:
            raise StupidProgrammerException("Missing payout pattern match in blackjack.payout()")

def bet_hand(player : Hand, dealer : Hand, bet : int, win_odds : PayoutOrd=PayoutOrd.ONE_ONE) -> int:
    """
    Given two hands, modifies a bet depending on the value comparison.

    Complexity: O(n) for number of cards
    """

    # As you read this function you'll notice an unintuitive call to payout(). That function computes the winnings on top of the original bet. This function encompasses the entire bet logic. A match function within a match function might seem confusing without this context so figured I'd mention it. Don't consider refactoring because the matches aren't the same.

    player_bust = is_bust(player)
    dealer_bust = is_bust(dealer)

    if player_bust and dealer_bust:
        return bet

    elif player_bust and not dealer_bust:
        return 0

    elif not player_bust and dealer_bust:
        return bet + payout(win_odds, bet)

    result = compare_hand(player, dealer)
    match result:
        case Ordinal.EQ:
            return bet
        case Ordinal.LT:
            return 0
        case Ordinal.GT:
            return bet + payout(win_odds, bet)
        case _:
            raise StupidProgrammerException("Missing pattern match in blackjack.bet_hand()")


def winnings(hands : Split, dealer : Hand, bet : int) -> int:
    """
    Computes bet winnings per hand split against the dealer.

    Complexity: O(n)
    """
    # naturals are 1:1 on split hands. fortunately this rule is accidentally built in already and nothing has to be done.
    return functools.reduce(
        lambda acc,hand: acc + bet_hand(hand, dealer, bet),
        hands,
        0
    )

def is_natural(hand: Hand) -> bool:
    # this is an indirect check. it works. checking directly through the cards themselves is needlessly harder to do.
    return len(hand) == constants.INITIAL_HAND_LEN and is_max(hand)

def is_bust(hand : Hand) -> bool:
    return hand_value(hand) > constants.MAX_HAND_VALUE

def is_max(hand : Hand) -> bool:
    return hand_value(hand) == constants.MAX_HAND_VALUE

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

def dealer_play(dealer : Hand, deck : Deck):
    i = len(dealer)
    while hand_value(dealer) < constants.DEALER_STOP and i <= constants.MAX_HAND_LEN:
        cards.take_card(dealer, deck)
        i += 1

    if i > constants.MAX_HAND_LEN:
        raise StupidProgrammerException("somehow the dealer keeps taking cards. infinite loop prevented.")
