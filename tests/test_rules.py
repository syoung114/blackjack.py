import pytest

import blackjack.rules as rules
import blackjack.cards as cards

import tests.helper_hands as hands

# /imports
#######################################################################################
## hand values

@pytest.mark.parametrize("a,b,ex", [
    (1, 0, rules.Ordinal.GT),
    (0, 0, rules.Ordinal.EQ),
    (0, 1, rules.Ordinal.LT)
])
def test_compare(a, b, ex):
    # note I know about comparing floating points but using floating point numbers aren't our intention. blackjack is largely discrete.
    assert rules.compare(a,b) == ex

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
    assert rules.hand_value(hand) == ex

def test_hand_value_whole_deck(fix_deck_alphabetical_52):
    # I got 340 using calculator
    assert rules.hand_value(fix_deck_alphabetical_52) == 340

@pytest.mark.parametrize("lhand,rhand,ex", [
    # identical low card
    (hands.hand_2H(), hands.hand_2H(), rules.Ordinal.EQ),
    # different suit
    (hands.hand_2H(), hands.hand_2D(), rules.Ordinal.EQ),
    # two cards each
    (hands.hand_2C2D(), hands.hand_2C2D(), rules.Ordinal.EQ),
    # lhand < rhand, different lengths
    (hands.hand_2H(), hands.hand_2C2D(), rules.Ordinal.LT),
    # inverse of previous
    (hands.hand_2C2D(), hands.hand_2H(), rules.Ordinal.GT),
    # natural 21 vs regular 21
    (hands.hand_blackjack_ace_up(), cards.parse_hand("7C 7D 7H"), rules.Ordinal.EQ),
    # natural 21 vs most cards without bust
    (hands.hand_blackjack_ace_down(), cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H"), rules.Ordinal.EQ),
    # single ace vs 2
    (cards.parse_hand("AC"), hands.hand_2H(), rules.Ordinal.GT),
    # single ace vs 10
    (cards.parse_hand("AC"), cards.parse_hand("10C"), rules.Ordinal.GT),
    # single ace vs unnatural 11
    (cards.parse_hand("AC"), cards.parse_hand("2C 9C"), rules.Ordinal.EQ),
    # both empty
    (hands.hand_empty(), hands.hand_empty(), rules.Ordinal.EQ)
])
def test_compare_hand(lhand, rhand, ex):
    assert rules.compare_hand(lhand,rhand) == ex

def test_compare_hand_extreme_gt(fix_deck_alphabetical_52):
    assert rules.compare_hand(fix_deck_alphabetical_52, hands.hand_2C()) == rules.Ordinal.GT

def test_compare_hand_extreme_lt(fix_deck_alphabetical_52):
    assert rules.compare_hand(hands.hand_2C(), fix_deck_alphabetical_52) == rules.Ordinal.LT
