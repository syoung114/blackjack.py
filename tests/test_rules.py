from copy import deepcopy
import pytest

from blackjack import constants

from blackjack.exception.StupidProgrammerException import StupidProgrammerException

import blackjack.rules as rules
import blackjack.cards as cards

import tests.helper_hands as hands

from tests.fixtures_cards import *

# /imports
#######################################################################################
# init hand

def test_init_hand_fix(fix_deck_alphabetical_52):
    original = deepcopy(fix_deck_alphabetical_52)
    hand = rules.init_hand(fix_deck_alphabetical_52)

    assert len(original) - constants.INITIAL_HAND_LEN == len(fix_deck_alphabetical_52)
    # need to reverse the list (order matters) then check if the hand matches the now first n elements
    assert original[::-1][:constants.INITIAL_HAND_LEN] == list(hand)

# /init hand
#######################################################################################
## hand_value

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
    (hands.hand_blackjack_ace_up(), cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H"), rules.Ordinal.EQ),
    # blackjack vs blackjack
    (hands.hand_blackjack_ace_up(), hands.hand_blackjack_ace_down(), rules.Ordinal.EQ),
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

# /hand_value
#######################################################################################
# payouts (these depend on or relate to hand_value)

@pytest.mark.parametrize("payout,bet,ex", [
    # baseline tests. nothing fancy.
    (rules.PayoutOrd.ONE_ONE, 10, 10),
    (rules.PayoutOrd.THREE_TWO, 10, 15),
    (rules.PayoutOrd.TWO_ONE, 10, 20),
    # another bet to imply it works for all bets
    (rules.PayoutOrd.THREE_TWO, 300, 450),
    # testing what the fractional property of three_two does to bet of value 1. The online blackjack I've played rounds down.
    (rules.PayoutOrd.THREE_TWO, 1, 1),
    # using a float anyway despite type annotations
    (rules.PayoutOrd.THREE_TWO, 3.14, 4),
    (rules.PayoutOrd.TWO_ONE, 3.14, 6.28)
    # testing large int is irrelevant because bit sizes of ints are abstracted away in python
])
def test_payout(payout,bet,ex):
    assert rules.payout(payout, bet) == ex

@pytest.mark.parametrize("payout,bet,exception", [
    (rules.PayoutOrd.ONE_ONE, -10, ValueError),
    (None, 10, StupidProgrammerException),
])
def test_payout_exceptions(payout,bet,exception):
    with pytest.raises(exception):
        rules.payout(payout,bet)

##### payout() above, bet_hand() below,

@pytest.mark.parametrize("player,dealer,bet,ex", [
    # player and dealer busts, soft 17. note 9+8==17 (see definition of bust_2) which means the dealer isn't supposed to hit.
    (hands.hand_bust_1(), hands.hand_bust_2(), 10, 10),
    # player and dealer bust, more common version
    (hands.hand_bust_1(), hands.hand_bust_dealer(), 10, 10),
    # player busts but not dealer, dealer==21.
    (hands.hand_bust_1(), hands.hand_blackjack_ace_up(), 10, 0), 
    # player busts and not dealer, dealer==4
    (hands.hand_bust_1(), hands.hand_2C2D(), 10, 0),
    # player not bust but dealer bust, player==21
    (hands.hand_blackjack_ace_up(), hands.hand_bust_dealer(), 10, 30),
    # player not bust but dealer bust, player==4
    (hands.hand_2C2D(), hands.hand_bust_dealer(), 10, 30),
    # the following is for neither bust...
    # greater hand, equal lengths
    (hands.hand_18_len_2(), hands.hand_17_len_2(), 10, 30),
    # greater hand, equal length (2)
    (hands.hand_blackjack_ace_up(), cards.parse_hand("QC 10D"), 10, 30),
    # greater hand, greater length
    (cards.parse_hand("2C 2D 2H 2S 3C 3D 3H AS"), hands.hand_17_len_2(), 10, 30),
    # greater hand, smaller length
    (hands.hand_18_len_2(), hands.hand_17_len_3(), 10, 30),
    # lesser hand, equal lengths
    (hands.hand_17_len_2(), hands.hand_18_len_2(), 10, 0),
    # lesser hand, equal length (2)
    (cards.parse_hand("QC 10D"), hands.hand_blackjack_ace_down(), 10, 0),
    # lesser hand, greater length
    (hands.hand_17_len_3(), hands.hand_18_len_2(), 10, 0),
    # lesser hand, smaller length
    (hands.hand_17_len_2(), hands.hand_18_len_3(), 10, 0),
    # equal hand, equal length (1)
    (hands.hand_blackjack_ace_up(), hands.hand_blackjack_ace_down(), 10, 10),
    # equal hand, equal length (2)
    (hands.hand_blackjack_ace_down(), hands.hand_blackjack_ace_up(), 10, 10),
    # equal hand, equal length (3)
    (cards.parse_hand("10C 7D"), cards.parse_hand("9H 8S"), 10, 10),
    # equal hand, equal length (4)
    (cards.parse_hand("5H 9S 4C"), cards.parse_hand("10S 5H 3D"), 10, 10)

])
def test_bet_hand(player,dealer,bet,ex):
    # test cases about payout ord are redundant because that tests compare_hand not bet_hand.
    # I choose TWO_ONE because it's harder to create false positives and I want to avoid coupling THREE_TWO blackjack winnings
    assert rules.bet_hand(player,dealer,bet,win_odds=rules.PayoutOrd.TWO_ONE) == ex

## def test_bet_hand_exception()

# SEEALSO winnings() in the splits section below

# /payouts
#######################################################################################
# general values

@pytest.mark.parametrize("hand,ex", [
    (hands.hand_blackjack_ace_up(), True),
    (hands.hand_blackjack_ace_down(), True),
    # 21 but not natural
    (cards.parse_hand("10C 8D 3H"), False),
    # initial_hand size
    (hands.hand_2C2D(), False),
    (cards.parse_hand("AC AD"), False),
    #impossible to bust on initial hand
])
def test_is_natural(hand,ex):
    assert rules.is_natural(hand) == ex

@pytest.mark.parametrize("hand,ex", [
    (hands.hand_blackjack_ace_up(), True),
    (hands.hand_blackjack_ace_down(), True),
    # 21 but not natural
    (cards.parse_hand("10C 8D 3H"), True),
    # initial_hand size
    (hands.hand_2C2D(), False),
    # 22 bust
    (hands.hand_17_len_3() + cards.parse_hand("5S"), False),
])
def test_is_max(hand,ex):
    assert rules.is_max(hand) == ex

#######################################################################################
# insurance

@pytest.mark.parametrize("hand,ex", [
    (hands.hand_blackjack_ace_down(), False),
    (hands.hand_blackjack_ace_up(), True),
    (cards.parse_hand("AC 2D"), True),
    (cards.parse_hand("2C AD"), False),
    (hands.hand_2C2D(), False), # some hand with no aces.
    (cards.parse_hand("10C 8D 3H"), False), # this is a 21. dealer doesn't have three cards but good test nonetheless.
    (cards.parse_hand("AC"), True) # probably should be undefined but whatever
])
def test_is_insurable(hand,ex):
    assert rules.is_insurable(hand) == ex

@pytest.mark.parametrize("hand,bet,ex1,ex2", [
    (hands.hand_blackjack_ace_up(), 10, True, 30),
    (cards.parse_hand("AC2D"), 10, False, 0),
    # the following aren't insurable in blackjack but it's defined behavior in the function.
    (hands.hand_blackjack_ace_down(), 10, True, 30),
    (hands.hand_2C2D(), 10, False, 0),
])
def test_insure(hand,bet,ex1,ex2):
    result_success, result_winnings = rules.insure(hand,bet)
    assert result_success == ex1
    assert result_winnings == ex2

@pytest.mark.parametrize("bet,ex", [
    (10, 5),
    (5, 2),
    (0, 0)
])
def test_insurance_make_side_bet(bet,ex):
    assert rules.insurance_make_side_bet(bet) == ex

# /insurance
#######################################################################################
# splits

@pytest.mark.parametrize("hand,ex", [
    (hands.hand_2C2D(), True),
    (cards.parse_hand("2C3D"), False),
    (cards.parse_hand("10C JC"), False),
    (cards.parse_hand("JC QC"), False),
])
def test_can_split(hand,ex):
    assert rules.can_split(hand) == ex

@pytest.mark.parametrize("hand,deck,split_ex,deck_ex", [
    (cards.parse_hand("ACAD"), cards.parse_hand("2C3D"), [cards.parse_hand("AC3D"), cards.parse_hand("AD2C")], hands.hand_empty()),
    # spliting a hand reveals a hand which also is splitable. splitting again is not allowed.
    (hands.hand_2C2D(), cards.parse_hand("2SKS2H"), [cards.parse_hand("2C2H"), cards.parse_hand("2DKS")], cards.parse_hand("2S")),
    # this hand can't be split but it's defined behavior anyway
    (cards.parse_hand("2H3S"), cards.parse_hand("2C3D"), [cards.parse_hand("2H3D"), cards.parse_hand("3S2C")], hands.hand_empty()),
])
def test_init_split(hand,deck,split_ex,deck_ex):
    result_split = rules.init_split(hand,deck)
    assert result_split == split_ex
    assert deck == deck_ex

@pytest.mark.parametrize("split,dealer,bet,ex", [
    # one hand win vs dealer
    ([hands.hand_blackjack_ace_down()], hands.hand_2C2D(), 10, 20),
    # one hand loss vs dealer
    ([hands.hand_2C2D()], hands.hand_blackjack_ace_down(), 10, 0),
    # two hands, both win against dealer.
    ([hands.hand_18_len_3(), hands.hand_18_len_2()], hands.hand_17_len_3(), 10, 40),
    # two hands, left wins against dealer, right pushes.
    ([hands.hand_18_len_3(), hands.hand_17_len_2()], hands.hand_17_len_3(), 10, 30),
    # two hands, left wins against dealer, right loses.
    ([hands.hand_18_len_3(), cards.parse_hand("JC 6D")], hands.hand_17_len_3(), 10, 20),
    # two hands lose against the dealer
    (2*[hands.hand_2C2D()], hands.hand_17_len_3(), 10, 0),
    # order of splits certainly don't matter and probably won't change in future so not testing them.
])
def test_winnings(split,dealer,bet,ex):
    assert rules.winnings(split,dealer,bet) == ex

# /splits
#######################################################################################
# dealer

@pytest.mark.parametrize("dealer,deck,dealer_ex,deck_ex", [
    # natural. nothing changes.
    (hands.hand_blackjack_ace_down(), hands.hand_2C2D(), hands.hand_blackjack_ace_down(), hands.hand_2C2D()),
    (hands.hand_blackjack_ace_up(), hands.hand_2C2D(), hands.hand_blackjack_ace_up(), hands.hand_2C2D()),
    # abnormal amount of aces. only the aces after the first get compressed, which give seven.
    (hands.hand_empty(), 7*cards.parse_hand("AC"), 7*cards.parse_hand("AC"), hands.hand_empty()),
    # lots of cards starting from 2
    (hands.hand_2C2D(), cards.parse_hand("2H 2S 3C 3D 3H 3S 4C")[::-1], cards.parse_hand("2C 2D 2H 2S 3C 3D 3H"), cards.parse_hand("4C 3S")),
])
def test_dealer_play(dealer,deck,dealer_ex,deck_ex):
    rules.dealer_play(dealer,deck)
    assert dealer == dealer_ex
    assert deck == deck_ex
