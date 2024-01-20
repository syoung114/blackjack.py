from typing import NamedTuple, List, Deque
from collections import deque
from enum import Enum
from random import Random
import re
from blackjack.core import constants

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
    QUEEN = (12,10)
    KING = (13,10)

class Suit(Enum):
    # In blackjack suits don't have an inherent rank but they need one for enum. I've used alphabetical.
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4

class Card(NamedTuple):
    rank: Rank
    suit: Suit

# Type synonyms
Hand = List[Card]
Deck = Deque[Card] # deletions are more important than random access and linear traversal and we are likely using a random order of elements. A deque fits this use case better than a list.

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

def parse_hand(hs : str, fmt : str=r'([2-9]|10|J|Q|K|A)([CDHS])') -> Hand:
    """
    Converts a string representation into usable format.

    Complexity: O(n), probably
    """
    # TODO these should respect the fmt string.
    # performance really isn't a concern in this function. you probably shouldn't mention specific cards in blackjack. the motive for this function is to make testing a breeze. the reason this function isn't in tests/ is because there might be a use case (user input) later on where this function is needed.
    suit_map = {
        'C' : Suit.CLUB,
        'D' : Suit.DIAMOND,
        'H' : Suit.HEART,
        'S' : Suit.SPADE,
    }
    rank_map = {
        'A' : Rank.ACE,
        '2' : Rank.TWO,
        '3' : Rank.THREE,
        '4' : Rank.FOUR,
        '5' : Rank.FIVE,
        '6' : Rank.SIX,
        '7' : Rank.SEVEN,
        '8' : Rank.EIGHT,
        '9' : Rank.NINE,
        '10' : Rank.TEN,
        'J' : Rank.JACK,
        'Q' : Rank.QUEEN,
        'K' : Rank.KING,
    }
    matches = re.findall(fmt, hs)
    return [ Card(rank_map[r], suit_map[s]) for r,s in matches ]

def card_rank_ord(card : Card) -> int:
    """
    Returns the order of a card within its rank. For an ace, this is one. For a king, this is thirteen.

    Complexity: O(1)
    """
    return card[0].value[0]

def card_value(card : Card) -> int:
    """
    Returns the value of a given card.

    Complexity: O(1)
    """
    return card[0].value[1]
