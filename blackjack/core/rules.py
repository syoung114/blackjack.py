import functools

from typing import List
from enum import Enum

from blackjack.core import constants
from blackjack.core import cards

from blackjack.core.PayoutOdds import PayoutOdds
from blackjack.core.cards import Hand, Deck, Rank
from blackjack.core.casino import HouseRules, TraditionalRules
from blackjack.core.exception.StupidProgrammerException import StupidProgrammerException

class Ordinal(Enum):
    LT = -1
    EQ = 0
    GT = 1

# /core definitions
######################################################################################
# hands

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

def is_hard_hand(hand : Hand) -> bool:
    """
    Determines whether a hand is 'hard' or 'soft' according to blackjack language.

    Complexity: O(n)
    """
    aces_count = 0
    for card in hand:
        if card.rank == Rank.ACE:
            aces_count += 1
            if aces_count > 1:
                return True

    if aces_count == 1:
        return False

    return True

# /hands
#######################################################################################
# payouts

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

def bet_hand(player : Hand, dealer : Hand, bet : int, win_odds : PayoutOdds=PayoutOdds.ONE_ONE, house : HouseRules=TraditionalRules) -> int:
    """
    Given two hands, modifies a bet depending on the value comparison.

    Complexity: O(n) for number of cards
    """

    # As you read this function you'll notice an unintuitive call to win_payout(). That function computes the winnings on top of the original bet. This function encompasses the entire bet logic. A match function within a match function might seem confusing without this context so figured I'd mention it. Don't consider refactoring because the matches aren't the same.

    player_bust = is_bust(player)
    dealer_bust = is_bust(dealer)

    if player_bust and dealer_bust:
        return bet

    elif player_bust and not dealer_bust:
        return 0

    elif not player_bust and dealer_bust:
        return bet + house.win_payout(win_odds, bet)

    result = compare_hand(player, dealer)
    match result:
        case Ordinal.EQ:
            return bet
        case Ordinal.LT:
            return 0
        case Ordinal.GT:
            return bet + house.win_payout(win_odds, bet)
        case _:
            raise StupidProgrammerException("Missing pattern match in blackjack.bet_hand()")


def winnings(hands : List[Hand], dealer : Hand, bet : int) -> int:
    """
    Computes bet winnings per hand split against the dealer.

    Complexity: O(n)
    """
    # naturals are 1:1 on split hands. fortunately this rule is accidentally built in already and nothing has to be done.
    bet_splice = round(bet / len(hands)) # TODO not scalable to len > 2 hands, if that were possible. this calculation is based on the assumption that the bet was *= 2 at split. also theoretically possible division by zero
    return functools.reduce(
        lambda acc,hand: acc + bet_hand(hand, dealer, bet_splice),
        hands,
        0
    )

# /payouts
#######################################################################################
# misc values

def is_natural(hand: Hand) -> bool:
    # this is an indirect check. it works. checking directly through the cards themselves is needlessly harder to do.
    return len(hand) == constants.INITIAL_HAND_LEN and is_max(hand)

@functools.singledispatch
def is_bust(value : int) -> bool:
    return value > constants.MAX_HAND_VALUE

@is_bust.register(list)
def _(hand : Hand) -> bool:
    return is_bust(hand_value(hand))

@functools.singledispatch
def is_max(value : int) -> bool:
    return value == constants.MAX_HAND_VALUE

@is_max.register(list)
def _(hand : Hand) -> bool:
    return is_max(hand_value(hand))

# /misc values
#######################################################################################
# insurance

def is_insurable(hand : Hand) -> bool:
    # we can directly access the second card here but it's not shown to user. so this function pretends.
    return hand[0][0] == cards.Rank.ACE

def insurance_make_side_bet(bet) -> int:
    # TODO allow flexible adjusting depending on casino rules
    return round(bet / 2)

def insure(dealer : Hand, side_bet : int, house : HouseRules=TraditionalRules):
    if is_natural(dealer): # whereas a previous check might have observed just ace, this function observes entire hand
        return True, side_bet + house.win_payout(PayoutOdds.TWO_ONE, side_bet)
    else:
        return False, 0

# /insurance
#######################################################################################
# splits

def can_split(hand : Hand) -> bool:
    return cards.card_rank_ord(hand[0]) == cards.card_rank_ord(hand[1])

def init_split(hand : Hand, deck : Deck) -> List[Hand]:
    return [[card, deck.pop()] for card in hand]

# /splits
#######################################################################################
# dealer

def dealer_play(dealer : Hand, deck : Deck):
    """
    Hits cards until the hand value >= constants.MAX_HAND_LEN

    Complexity: O(n)

    Impure
    """
    i = len(dealer)
    while hand_value(dealer) < constants.DEALER_STOP and i <= constants.MAX_HAND_LEN:
        cards.take_card(dealer, deck)
        i += 1

    if i > constants.MAX_HAND_LEN:
        raise StupidProgrammerException("somehow the dealer keeps taking cards. infinite loop prevented.")
