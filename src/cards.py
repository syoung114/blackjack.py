from typing import NamedTuple, List, Deque, Type
from collections import deque
from enum import Enum
from random import Random, sample
import re

class Rank(Enum):
    # We can keep track of ordinal and card value using tuple.
    TWO = (0,2)
    THREE = (1,3)
    FOUR = (2,4)
    FIVE = (3,5)
    SIX = (4,6)
    SEVEN = (5,7)
    EIGHT = (6,8)
    NINE = (7,9)
    TEN = (8,10)
    JACK = (9,10)
    KING = (10,10)
    QUEEN = (11,10)
    ACE = (12,11)

class Suit(Enum):
    # In blackjack suits don't have an inherent rank but they need one for enum. I've used alphabetical.
    CLUB = 1
    DIAMOND = 2
    HEART = 3
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

# Type synonyms
Hand = List[Card]
Deck = Deque[Card] # deletions are more important than random access and linear traversal and we are likely using a random order of elements. A deque fits this use case than a list.

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
        for (r,_) in range(len(f_hand), len(t_hand)):
            t_sum += r

    elif len(t_hand) < len(f_hand):
        for (r,_) in range(len(t_hand), len(f_hand)):
            f_sum += r

    return compare(t_sum, f_sum)

def parse_hand(hs : str, fmt : str=r'([2-9]|10|J|Q|K|A)([CDHS])') -> Hand:
    """
    Converts a string representation into usable format.

    Complexity: O(n), probably
    """
    matches = re.findall(fmt, hs)
    return [ Card(r,s) for r,s in matches ]

def make_deck_ordered() -> Deck:
    """
    Creates a standard deck of cards.

    Complexity: O(sr)
    """
    deck = deque()
    for suit in Suit:
        for rank in Rank:
            deck.append(Card(rank,suit))
    return deck

def make_deck_unordered(rseed : Random) -> Deck:
    """
    Creates a shuffled deck of cards.

    @arg rseed The generator for random shuffling. Required to maintain pure interface.

    Complexity: O(sr log sr)
    """
    # I had an idea inspired by hash maps where you attempt random insertion while below a load factor, then swap to a more linear mechanism when that factor is exceeded. This would be more scalable but there are only 52 cards in a deck so not worth it.

    DECK_SIZE = 52

    indices = [i for i in range(DECK_SIZE)]
    rseed.shuffle(indices)

    # make ordered deck as list to base the random deck off of
    ord_deck = [None] * DECK_SIZE
    i = 0
    for suit in Suit:
        for rank in Rank:
            ord_deck[i] = Card(rank,suit)
            print(f"{i} {ord_deck[i]}")
            i += 1
    
    unord_deck = deque()

    for i in indices:
        unord_deck.append(ord_deck[i])

    return unord_deck

def take_card(hand : Hand, deck : Deck):
    """
    Moves a card from the deck into a hand.

    Complexity: O(1)

    Impure
    """
    hand.append(deck.pop())

def init_hand(deck : Deck) -> Hand:
    """
    Takes two cards from the deck, starting from the last key.

    Complexity: O(1)
    """
    h = []

    take_card(h, deck)
    take_card(h, deck)

    return h
