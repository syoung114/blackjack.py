import pytest
import random
from copy import deepcopy

import blackjack.constants as constants
import blackjack.cards as cards

import tests.helper_hands as hands
from tests.fixtures_cards import *
#import tests.fixtures_cards as fixtures_cards

from blackjack.cards import Card, Rank, Suit

# /imports
########################################################################################
# parse_hand

@pytest.mark.parametrize("raw,ex", [
    # one card gives a hand of the same card
    ("2C", hands.hand_2C()),
    # two identical cards. invalid in blackjack but not this function's concern
    ("2C2C", [Card(Rank.TWO, Suit.CLUB), Card(Rank.TWO, Suit.CLUB)]),
    # four cards over all suits
    ("2C3D4H5S", [Card(Rank.TWO, Suit.CLUB), Card(Rank.THREE, Suit.DIAMOND), Card(Rank.FOUR, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]),
    # low hand
    ("2C2D", hands.hand_2C2D()),
    # high hand
    ("10CJC", [Card(Rank.TEN, Suit.CLUB), Card(Rank.JACK, Suit.CLUB)]),
    # natural/blackjack example
    ("ACJC", hands.hand_blackjack_ace_up()),
    # arbitrary delimiter
    ("2C 2D", hands.hand_2C2D()),
    # valid interleave
    ("22C", hands.hand_2C()),
    # invalid interleave
    ("2|C", hands.hand_empty()),
    # empty string
    ("", hands.hand_empty())
])
def test_parse_hand(raw, ex):
    # a lot of tests depend on this function (because manually defining a card through Card tuple is painful) so it's important to get right.
    assert list(cards.parse_hand(raw)) == list(ex)

def test_parse_hand_deck_fixture(fix_deck_alphabetical_52):
    # I'm all for writing a new function if it means I can use existing fixture
    assert \
        list(cards.parse_hand("AC2C3C4C5C6C7C8C9C10CJCQCKCAD2D3D4D5D6D7D8D9D10DJDQDKDAH2H3H4H5H6H7H8H9H10HJHQHKHAS2S3S4S5S6S7S8S9S10SJSQSKS")) \
        == list(fix_deck_alphabetical_52)

# /parse_hand
########################################################################################
# card properties

def test_card_rank(fix_deck_alphabetical_52):
    for card in fix_deck_alphabetical_52:
        assert cards.card_rank_ord(card) == card[0].value[0]

def test_card_value(fix_deck_alphabetical_52):
    for card in fix_deck_alphabetical_52:
        assert cards.card_value(card) == card[0].value[1]

def test_card_suit_clubs(fix_deck_clubs_12):
    for card in fix_deck_clubs_12:
        assert card[1] == cards.Suit.CLUB

def test_card_suit_diamonds(fix_deck_diamonds_12):
    for card in fix_deck_diamonds_12:
        assert card[1] == cards.Suit.DIAMOND

# /card properties
#######################################################################################
# decks

def test_make_deck_ordered(fix_deck_alphabetical_52):
    basis = cards.make_deck_ordered()
    assert len(cards.Rank) * len(cards.Suit) == constants.DECK_SIZE
    assert len(basis) == len(fix_deck_alphabetical_52)
    assert list(basis) == list(fix_deck_alphabetical_52)

def test_make_deck_unordered(fix_rseed_zero_deck):
    assert len(cards.Rank) * len(cards.Suit) == constants.DECK_SIZE
    assert cards.make_deck_unordered(random.Random(0)) == fix_rseed_zero_deck

@pytest.mark.parametrize("hand,deck,hex,dex", [
    # empty hand, deck has one card -> transfers that card over
    (hands.hand_empty(), hands.hand_2C(), hands.hand_2C(),hands.hand_empty()),
    # empty hand, deck has two cards -> last card is inserted into hand
    (hands.hand_empty(), hands.hand_2C2D(), hands.hand_2D(), hands.hand_2C()),
    # hand has one card, deck has one card -> hand has two cards, deck has none
    (hands.hand_2C(), hands.hand_2D(), hands.hand_2C2D(), hands.hand_empty()),
    # hand has two cards, deck has one card -> hand has three cards, deck has none
    (hands.hand_2C2D(), hands.hand_2H(), hands.hand_2C2D() + hands.hand_2H(), hands.hand_empty()),
    # hand has one card, deck has two cards -> hand has two cards, deck has two cards
    (hands.hand_2C(), hands.hand_2D() + hands.hand_2H(), hands.hand_2C() + hands.hand_2H(), hands.hand_2D())
])
def test_take_card(hand, deck, hex, dex):
    cards.take_card(hand, deck)
    assert list(hand) == list(hex)
    assert list(deck) == list(dex)

@pytest.mark.parametrize("hand,deck,exception", [
    (hands.hand_empty(), hands.hand_empty(), IndexError),
    (hands.hand_2C(), hands.hand_empty(), IndexError)
])
def test_take_card_exceptions(hand,deck,exception):
    with pytest.raises(exception):
        cards.take_card(hand,deck)

def test_take_card_entire_deck(fix_deck_alphabetical_52):
    original = deepcopy(fix_deck_alphabetical_52)
    hand = hands.hand_empty()
    i = 0
    while fix_deck_alphabetical_52:
        if i > len(original):
            assert False, f"iterations exceeded length of deck: {len(original)}"

        cards.take_card(hand, fix_deck_alphabetical_52)
        i += 1

    assert len(fix_deck_alphabetical_52) == 0
    assert hand[::-1] == list(original)

## /decks
#######################################################################################
## hand values

@pytest.mark.parametrize("a,b,ex", [
    (1, 0, cards.Ordinal.GT),
    (0, 0, cards.Ordinal.EQ),
    (0, 1, cards.Ordinal.LT)
])
def test_compare(a, b, ex):
    # note I know about comparing floating points but using floating point numbers aren't our intention. blackjack is largely discrete.
    assert cards.compare(a,b) == ex

@pytest.mark.parametrize("hand,ex", [
    # really low hand, no aces
    (hands.hand_2C2D(), 4),
    # another hand, no aces. fibonacci for no reason.
    (cards.parse_hand("3C 5D 8H"), 16),
    # same hand as before but reversed.
    (cards.parse_hand("8H 5D 3C"), 16),
    # same hand as beforebefore but forward modulus
    (cards.parse_hand("8H 3C 5D"), 16),
    # same hand as beforebeforebefore but + 1.
    (cards.parse_hand("4C 5D 8H"), 17),
    # same hand as beforebeforebeforebefore but - 1.
    (cards.parse_hand("2C 5D 8H"), 15),
    # two face cards.
    (cards.parse_hand("JC QD"), 20),
    # two face cards and an ace.
    (cards.parse_hand("JC QD AH"), 21),
    # all face cards. don't care about bust.
    (cards.parse_hand("JC QD KS"), 30),
    # all face cards and ten. don't care about bust.
    (cards.parse_hand("JC QD KS 10H"), 40),
    # all face cards and ten and an ace. don't care about bust.
    (cards.parse_hand("JC QD KH 10H AS"), 41),
    # 21 without any aces 1
    (cards.parse_hand("7C 7D 7H"), 21),
    # 21 without any aces 2
    (cards.parse_hand("10C 3D 3H 5S"), 21),
    # natural/blackjack 1
    (hands.hand_blackjack_ace_up(), 21),
    # natural/blackjack 2
    (hands.hand_blackjack_ace_down(), 21),
    # various cards with one ace
    (hands.hand_2C2D() + cards.parse_hand("AH"), 15),
    # two aces
    (cards.parse_hand("AC AD"), 12),
    # two aces and a lower card
    (cards.parse_hand("AC AD 2H"), 14),
    # two aces and a nine for max 21
    (cards.parse_hand("AC AD 9H"), 21),
    # all four aces
    (cards.parse_hand("AC AD AH AS"), 14),
    # most cards without busting
    (cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H"), 21),
    # most cards without busting, plus another card
    (cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H 3S"), 24),
    # empty hand
    (hands.hand_empty(), 0)
])
def test_hand_value(hand,ex):
    assert cards.hand_value(hand) == ex

def test_hand_value_whole_deck(fix_deck_alphabetical_52):
    # I got 340 using calculator
    assert cards.hand_value(fix_deck_alphabetical_52) == 340


@pytest.mark.parametrize("lhand,rhand,ex", [
    # identical low card
    (hands.hand_2H(), hands.hand_2H(), cards.Ordinal.EQ),
    # different suit
    (hands.hand_2H(), hands.hand_2D(), cards.Ordinal.EQ),
    # two cards each
    (hands.hand_2C2D(), hands.hand_2C2D(), cards.Ordinal.EQ),
    # lhand < rhand, different lengths
    (hands.hand_2H(), hands.hand_2C2D(), cards.Ordinal.LT),
    # inverse of previous
    (hands.hand_2C2D(), hands.hand_2H(), cards.Ordinal.GT),
    # natural 21 vs regular 21
    (hands.hand_blackjack_ace_up(), cards.parse_hand("7C 7D 7H"), cards.Ordinal.EQ),
    # natural 21 vs most cards without bust
    (hands.hand_blackjack_ace_down(), cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H"), cards.Ordinal.EQ),
    # single ace vs 2
    (cards.parse_hand("AC"), hands.hand_2H(), cards.Ordinal.GT),
    # single ace vs 10
    (cards.parse_hand("AC"), cards.parse_hand("10C"), cards.Ordinal.GT),
    # single ace vs unnatural 11
    (cards.parse_hand("AC"), cards.parse_hand("2C 9C"), cards.Ordinal.EQ),
    # both empty
    (hands.hand_empty(), hands.hand_empty(), cards.Ordinal.EQ)
])
def test_compare_hand(lhand, rhand, ex):
    assert cards.compare_hand(lhand,rhand) == ex

def test_compare_hand_extreme_gt(fix_deck_alphabetical_52):
    assert cards.compare_hand(fix_deck_alphabetical_52, hands.hand_2C()) == cards.Ordinal.GT

def test_compare_hand_extreme_lt(fix_deck_alphabetical_52):
    assert cards.compare_hand(hands.hand_2C(), fix_deck_alphabetical_52) == cards.Ordinal.LT
