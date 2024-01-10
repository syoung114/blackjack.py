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
    assert list(cards.make_deck_unordered(random.Random(0))) == list(fix_rseed_zero_deck)

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
