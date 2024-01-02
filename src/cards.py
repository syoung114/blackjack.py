from typing import NamedTuple, List, Deque, Type
from collections import deque
from enum import Enum
from random import Random, sample
import re
from . import constants

class Rank(Enum):
    # We can keep track of ordinal and card value using tuple.
    ACE = (1,11)
    TWO = (2,2)
    THREE = (3,3)
    FOUR = (4,4)
    FIVE = (5,5)
    SIX = (6,6)
    SEVEN = (7,7)
    EIGHT = (8,8)
    NINE = (9,9)
    TEN = (10,10)
    JACK = (11,10)
    KING = (12,10)
    QUEEN = (13,10)

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

# Type synonyms
Hand = List[Card]
Deck = Deque[Card] # deletions are more important than random access and linear traversal and we are likely using a random order of elements. A deque fits this use case than a list.

def card_rank_ord(card : Card) -> int:
    return card[0].value[0]

def card_value(card : Card) -> int:
    """
    Returns the value of a given card.

    Complexity: O(1)
    """
    return card[0].value[1]

def hand_value(hand : Hand) -> int:
    """
    Accumulates the cards in a hand, including ace rules. Does not handle busts. When there is an ace, it adds 11 until there is a bust, and 1 thereafter, no matter if adding 1 is a bust.

    Complexity: O(n)
    """
    # could refactor into functools.reduce but it might be less understandable.
    acc = 0
    for card in hand:
        rank_ord = card_rank_ord(card)
        val = card_value(card)

        # The second OR operand is for aces logic. If it is an ace and eleven fits into the hand without busting, add eleven else add one
        if rank_ord != Rank.ACE.value[0] or acc + val <= constants.MAX_HAND_VALUE:
            acc += val
        else:
            acc += rank_ord

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

def compare_hand(l_hand : Hand, r_hand : Hand) -> Ordinal:
    """
    Indicates which hand has the greater cumulative hand value.

    Complexity: O(n)
    """
    l_sum = 0
    r_sum = 0

    # count in parallel until we reach end of shorter hand
    for card1,card2 in zip(l_hand,r_hand):
        l_sum += card_value(card1) 
        r_sum += card_value(card2) 

    # continue for the larger hand, if lengths not equal
    if len(l_hand) > len(r_hand):
        # note that slicing isn't O(1) but it's most intuitive approach. more performant would be indexing through range.
        for card in l_hand[:len(r_hand)]:
            l_sum += card_value(card)

    elif len(l_hand) < len(r_hand):
        for card in r_hand[:len(l_hand)]:
            r_sum += card_value(card)

    return compare(l_sum, r_sum)

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

    indices = [i for i in range(constants.DECK_SIZE)]
    rseed.shuffle(indices)

    # make ordered deck as list to base the random deck off of. The card chosen is a placeholder because None is apparently unpolymorphic to named tuples.
    ord_deck = [Card(Rank.TWO,Suit.CLUB)] * constants.DECK_SIZE
    i = 0
    for suit in Suit:
        for rank in Rank:
            ord_deck[i] = Card(rank,suit)
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
