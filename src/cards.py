from typing import NamedTuple, List, Dict
from enum import Enum

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    JACK = 10
    QUEEN = 10
    KING = 10
    ACE = 11

class Suit(Enum):
    # In blackjack suits don't have an inherent rank but I've arbitrarily given them one for random generation
    DIAMOND = 1
    HEART = 2
    CLUB = 3
    SPADE = 4

class Card(NamedTuple):
    rank: Rank
    suit: Suit

class Ordinal(Enum):
    LT = -1
    EQ = 0
    GT = 1

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

type Hand = List[Card]
type Deck = Dict[int, Hand]

def make_deck_ordered() -> Deck:
    """
    Creates a standard deck of cards.

    Complexity: O(sr)
    """
    deck = {}
    for suit in Suit:
        for rank in Rank:
            deck[len(deck)] = Card(rank,suit)
    return deck

def make_deck_unordered(rseed : Random) -> Deck:
    """
    Creates a shuffled deck of cards.

    @arg rseed The generator for random shuffling. Required for pure interface.

    Complexity: O(sr log sr)
    """
    # I had an idea inspired by hash maps where you attempt random insertion while below a load factor, then swap to a more linear mechanism when that factor is exceeded. This would be more scalable but there are only 52 cards in a deck so not worth it.
    cards = make_deck_ordered().values()
    return dict(enumerate(
        rseed.shuffle(cards)
    ))

def take_card(at : int, hand : Hand, deck : Deck):
    """
    Moves a card from the deck into a hand.

    Complexity: O(1)
    """
    hand.append(deck[at])
    del deck[at]

def compare_hand(t_hand : Hand, f_hand : Hand) -> Ordinal:
    """
    Indicates which hand has the greater cumulative hand value.

    Complexity: O(n)
    """
    t_sum = 0
    f_sum = 0

    # count in parallel until we reach end of shorter hand
    for (r1,_),(r2,_) in zip(f_hand,t_hand):
        t_sum += r1
        f_sum += r2

    # continue for the larger hand, if lengths not equal
    if len(t_hand) > len(f_hand):
        for (r,_) in range(len(f_hand), len(t_hand))
            t_sum += r

    elif len(t_hand) < len(f_hand):
        for (r,_) in range(len(t_hand), len(f_hand)):
            f_sum += r

    return compare(t_sum, f_sum)
