from copy import deepcopy
import pytest

from blackjack.core import constants
from blackjack.core import rules, cards
from blackjack.core.PayoutOdds import PayoutOdds
from blackjack.core.exception.StupidProgrammerException import StupidProgrammerException

from tests.core import helper_hands
from tests.core.fixtures_cards import *

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
    (helper_hands.hand_2C2D(), 4),
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
    (helper_hands.hand_blackjack_ace_up(), 21),
    # natural/blackjack 2
    (helper_hands.hand_blackjack_ace_down(), 21),
    # various cards with one ace
    (helper_hands.hand_2C2D() + cards.parse_hand("AH"), 15),
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
    (helper_hands.hand_empty(), 0)
])
def test_hand_value(hand,ex):
    assert rules.hand_value(hand) == ex

def test_hand_value_whole_deck(fix_deck_alphabetical_52):
    # I got 340 using calculator
    assert rules.hand_value(fix_deck_alphabetical_52) == 340

@pytest.mark.parametrize("lhand,rhand,ex", [
    # identical low card
    (helper_hands.hand_2H(), helper_hands.hand_2H(), rules.Ordinal.EQ),
    # different suit
    (helper_hands.hand_2H(), helper_hands.hand_2D(), rules.Ordinal.EQ),
    # two cards each
    (helper_hands.hand_2C2D(), helper_hands.hand_2C2D(), rules.Ordinal.EQ),
    # lhand < rhand, different lengths
    (helper_hands.hand_2H(), helper_hands.hand_2C2D(), rules.Ordinal.LT),
    # inverse of previous
    (helper_hands.hand_2C2D(), helper_hands.hand_2H(), rules.Ordinal.GT),
    # natural 21 vs regular 21
    (helper_hands.hand_blackjack_ace_up(), cards.parse_hand("7C 7D 7H"), rules.Ordinal.EQ),
    # natural 21 vs most cards without bust
    (helper_hands.hand_blackjack_ace_up(), cards.parse_hand("AC AD AH AS 2C 2D 2H 2S 3C 3D 3H"), rules.Ordinal.EQ),
    # blackjack vs blackjack
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_blackjack_ace_down(), rules.Ordinal.EQ),
    # single ace vs 2
    (cards.parse_hand("AC"), helper_hands.hand_2H(), rules.Ordinal.GT),
    # single ace vs 10
    (cards.parse_hand("AC"), cards.parse_hand("10C"), rules.Ordinal.GT),
    # single ace vs unnatural 11
    (cards.parse_hand("AC"), cards.parse_hand("2C 9C"), rules.Ordinal.EQ),
    # both empty
    (helper_hands.hand_empty(), helper_hands.hand_empty(), rules.Ordinal.EQ)
])
def test_compare_hand(lhand, rhand, ex):
    assert rules.compare_hand(lhand,rhand) == ex

def test_compare_hand_extreme_gt(fix_deck_alphabetical_52):
    assert rules.compare_hand(fix_deck_alphabetical_52, helper_hands.hand_2C()) == rules.Ordinal.GT

def test_compare_hand_extreme_lt(fix_deck_alphabetical_52):
    assert rules.compare_hand(helper_hands.hand_2C(), fix_deck_alphabetical_52) == rules.Ordinal.LT

# /hand_value
#######################################################################################
# other hand methods

@pytest.mark.parametrize("hand,ex", [
    (cards.parse_hand("ACAD"), True),
    (cards.parse_hand("AC2D"), False),
    (helper_hands.hand_2C2D(), True)
])
def test_is_hard_hand(hand,ex):
    assert rules.is_hard_hand(hand) == ex

# /other hand methods
#######################################################################################
# payouts (these depend on or relate to hand_value)

@pytest.mark.parametrize("player,dealer,bet,ex", [
    # player and dealer busts, soft 17. note 9+8==17 (see definition of bust_2) which means the dealer isn't supposed to hit.
    (helper_hands.hand_bust_1(), helper_hands.hand_bust_2(), 10, 10),
    # player and dealer bust, more common version
    (helper_hands.hand_bust_1(), helper_hands.hand_bust_dealer(), 10, 10),
    # player busts but not dealer, dealer==21.
    (helper_hands.hand_bust_1(), helper_hands.hand_blackjack_ace_up(), 10, 0), 
    # player busts and not dealer, dealer==4
    (helper_hands.hand_bust_1(), helper_hands.hand_2C2D(), 10, 0),
    # player not bust but dealer bust, player==21
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_bust_dealer(), 10, 20),
    # player not bust but dealer bust, player==4
    (helper_hands.hand_2C2D(), helper_hands.hand_bust_dealer(), 10, 20),
    # the following is for neither bust...
    # greater hand, equal lengths
    (helper_hands.hand_18_len_2(), helper_hands.hand_17_len_2(), 10, 20),
    # greater hand, equal length (2)
    (helper_hands.hand_blackjack_ace_up(), cards.parse_hand("QC 10D"), 10, 20),
    # greater hand, greater length
    (cards.parse_hand("2C 2D 2H 2S 3C 3D 3H AS"), helper_hands.hand_17_len_2(), 10, 20),
    # greater hand, smaller length
    (helper_hands.hand_18_len_2(), helper_hands.hand_17_len_3(), 10, 20),
    # lesser hand, equal lengths
    (helper_hands.hand_17_len_2(), helper_hands.hand_18_len_2(), 10, 0),
    # lesser hand, equal length (2)
    (cards.parse_hand("QC 10D"), helper_hands.hand_blackjack_ace_down(), 10, 0),
    # lesser hand, greater length
    (helper_hands.hand_17_len_3(), helper_hands.hand_18_len_2(), 10, 0),
    # lesser hand, smaller length
    (helper_hands.hand_17_len_2(), helper_hands.hand_18_len_3(), 10, 0),
    # equal hand, equal length (1)
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_blackjack_ace_down(), 10, 10),
    # equal hand, equal length (2)
    (helper_hands.hand_blackjack_ace_down(), helper_hands.hand_blackjack_ace_up(), 10, 10),
    # equal hand, equal length (3)
    (cards.parse_hand("10C 7D"), cards.parse_hand("9H 8S"), 10, 10),
    # equal hand, equal length (4)
    (cards.parse_hand("5H 9S 4C"), cards.parse_hand("10S 5H 3D"), 10, 10)

])
def test_bet_hand_ONE_ONE(player,dealer,bet,ex):
    # test cases about win_payout ord are redundant because that tests compare_hand not bet_hand.
    assert rules.bet_hand(player,dealer,bet,win_odds=PayoutOdds.ONE_ONE) == ex

@pytest.mark.parametrize("player,dealer,bet,ex", [
    # player and dealer busts, soft 17. note 9+8==17 (see definition of bust_2) which means the dealer isn't supposed to hit.
    (helper_hands.hand_bust_1(), helper_hands.hand_bust_2(), 10, 10),
    # player and dealer bust, more common version
    (helper_hands.hand_bust_1(), helper_hands.hand_bust_dealer(), 10, 10),
    # player busts but not dealer, dealer==21.
    (helper_hands.hand_bust_1(), helper_hands.hand_blackjack_ace_up(), 10, 0), 
    # player busts and not dealer, dealer==4
    (helper_hands.hand_bust_1(), helper_hands.hand_2C2D(), 10, 0),
    # player not bust but dealer bust, player==21
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_bust_dealer(), 10, 30),
    # player not bust but dealer bust, player==4
    (helper_hands.hand_2C2D(), helper_hands.hand_bust_dealer(), 10, 30),
    # the following is for neither bust...
    # greater hand, equal lengths
    (helper_hands.hand_18_len_2(), helper_hands.hand_17_len_2(), 10, 30),
    # greater hand, equal length (2)
    (helper_hands.hand_blackjack_ace_up(), cards.parse_hand("QC 10D"), 10, 30),
    # greater hand, greater length
    (cards.parse_hand("2C 2D 2H 2S 3C 3D 3H AS"), helper_hands.hand_17_len_2(), 10, 30),
    # greater hand, smaller length
    (helper_hands.hand_18_len_2(), helper_hands.hand_17_len_3(), 10, 30),
    # lesser hand, equal lengths
    (helper_hands.hand_17_len_2(), helper_hands.hand_18_len_2(), 10, 0),
    # lesser hand, equal length (2)
    (cards.parse_hand("QC 10D"), helper_hands.hand_blackjack_ace_down(), 10, 0),
    # lesser hand, greater length
    (helper_hands.hand_17_len_3(), helper_hands.hand_18_len_2(), 10, 0),
    # lesser hand, smaller length
    (helper_hands.hand_17_len_2(), helper_hands.hand_18_len_3(), 10, 0),
    # equal hand, equal length (1)
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_blackjack_ace_down(), 10, 10),
    # equal hand, equal length (2)
    (helper_hands.hand_blackjack_ace_down(), helper_hands.hand_blackjack_ace_up(), 10, 10),
    # equal hand, equal length (3)
    (cards.parse_hand("10C 7D"), cards.parse_hand("9H 8S"), 10, 10),
    # equal hand, equal length (4)
    (cards.parse_hand("5H 9S 4C"), cards.parse_hand("10S 5H 3D"), 10, 10)

])
def test_bet_hand_TWO_ONE(player,dealer,bet,ex):
    # test cases about win_payout ord are redundant because that tests compare_hand not bet_hand.
    assert rules.bet_hand(player,dealer,bet,win_odds=PayoutOdds.TWO_ONE) == ex

## def test_bet_hand_exception()

# SEEALSO winnings() in the splits section below

# /payouts
#######################################################################################
# general values

@pytest.mark.parametrize("hand,ex", [
    (helper_hands.hand_blackjack_ace_up(), True),
    (helper_hands.hand_blackjack_ace_down(), True),
    # 21 but not natural
    (cards.parse_hand("10C 8D 3H"), False),
    # initial_hand size
    (helper_hands.hand_2C2D(), False),
    (cards.parse_hand("AC AD"), False),
    #impossible to bust on initial hand
])
def test_is_natural(hand,ex):
    assert rules.is_natural(hand) == ex

@pytest.mark.parametrize("hand,ex", [
    (helper_hands.hand_blackjack_ace_up(), True),
    (helper_hands.hand_blackjack_ace_down(), True),
    # 21 but not natural
    (cards.parse_hand("10C 8D 3H"), True),
    # initial_hand size
    (helper_hands.hand_2C2D(), False),
    # 22 bust
    (helper_hands.hand_17_len_3() + cards.parse_hand("5S"), False),
])
def test_is_max(hand,ex):
    assert rules.is_max(hand) == ex

#######################################################################################
# insurance

@pytest.mark.parametrize("hand,ex", [
    (helper_hands.hand_blackjack_ace_down(), False),
    (helper_hands.hand_blackjack_ace_up(), True),
    (cards.parse_hand("AC 2D"), True),
    (cards.parse_hand("2C AD"), False),
    (helper_hands.hand_2C2D(), False), # some hand with no aces.
    (cards.parse_hand("10C 8D 3H"), False), # this is a 21. dealer doesn't have three cards but good test nonetheless.
    (cards.parse_hand("AC"), True) # probably should be undefined but whatever
])
def test_is_insurable(hand,ex):
    assert rules.is_insurable(hand) == ex

@pytest.mark.parametrize("hand,bet,ex1,ex2", [
    (helper_hands.hand_blackjack_ace_up(), 10, True, 30),
    (cards.parse_hand("AC2D"), 10, False, 0),
    # the following aren't insurable in blackjack but it's defined behavior in the function.
    (helper_hands.hand_blackjack_ace_down(), 10, True, 30),
    (helper_hands.hand_2C2D(), 10, False, 0),
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
    (helper_hands.hand_2C2D(), True),
    (cards.parse_hand("2C3D"), False),
    (cards.parse_hand("10C JC"), False),
    (cards.parse_hand("JC QC"), False),
])
def test_can_split(hand,ex):
    assert rules.can_split(hand) == ex

@pytest.mark.parametrize("hand,deck,split_ex,deck_ex", [
    (cards.parse_hand("ACAD"), cards.parse_hand("2C3D"), [cards.parse_hand("AC3D"), cards.parse_hand("AD2C")], helper_hands.hand_empty()),
    # spliting a hand reveals a hand which also is splitable. splitting again is not allowed.
    (helper_hands.hand_2C2D(), cards.parse_hand("2SKS2H"), [cards.parse_hand("2C2H"), cards.parse_hand("2DKS")], cards.parse_hand("2S")),
    # this hand can't be split but it's defined behavior anyway
    (cards.parse_hand("2H3S"), cards.parse_hand("2C3D"), [cards.parse_hand("2H3D"), cards.parse_hand("3S2C")], helper_hands.hand_empty()),
])
def test_init_split(hand,deck,split_ex,deck_ex):
    result_split = rules.init_split(hand,deck)
    assert result_split == split_ex
    assert deck == deck_ex

@pytest.mark.parametrize("split,dealer,bet,ex_winnings", [
    # one hand win vs dealer
    ([helper_hands.hand_18_len_2()], helper_hands.hand_2C2D(), 100, 200),
    # one hand push vs dealer
    ([helper_hands.hand_17_len_2()], helper_hands.hand_17_len_3(), 100, 100),
    # one hand loss vs dealer
    ([helper_hands.hand_2C2D()], helper_hands.hand_blackjack_ace_down(), 100, 0),
    # two hands, both win against dealer.
    ([helper_hands.hand_18_len_3(), helper_hands.hand_18_len_2()], helper_hands.hand_17_len_3(), 200, 400),
    # two hands, left wins against dealer, right pushes.
    ([helper_hands.hand_18_len_3(), helper_hands.hand_17_len_2()], helper_hands.hand_17_len_3(), 200, 300),
    # two hands, left wins against dealer, right loses.
    ([helper_hands.hand_18_len_3(), cards.parse_hand("JC 6D")], helper_hands.hand_17_len_3(), 200, 200),
    # two hands lose against the dealer
    (2*[helper_hands.hand_2C2D()], helper_hands.hand_17_len_3(), 200, 0),
    # order of splits certainly don't matter and probably won't change in future so not testing them.
])
def test_winnings(split,dealer,bet,ex_winnings):
    assert rules.winnings(split,dealer,bet) == ex_winnings

# /splits
#######################################################################################
# dealer

@pytest.mark.parametrize("dealer,deck,dealer_ex,deck_ex", [
    # natural. nothing changes.
    (helper_hands.hand_blackjack_ace_down(), helper_hands.hand_2C2D(), helper_hands.hand_blackjack_ace_down(), helper_hands.hand_2C2D()),
    (helper_hands.hand_blackjack_ace_up(), helper_hands.hand_2C2D(), helper_hands.hand_blackjack_ace_up(), helper_hands.hand_2C2D()),
    # abnormal amount of aces. only the aces after the first get compressed, which give seven.
    (helper_hands.hand_empty(), 7*cards.parse_hand("AC"), 7*cards.parse_hand("AC"), helper_hands.hand_empty()),
    # lots of cards starting from 2
    (helper_hands.hand_2C2D(), cards.parse_hand("2H 2S 3C 3D 3H 3S 4C")[::-1], cards.parse_hand("2C 2D 2H 2S 3C 3D 3H"), cards.parse_hand("4C 3S")),
])
def test_dealer_play(dealer,deck,dealer_ex,deck_ex):
    rules.dealer_play(dealer,deck)
    assert dealer == dealer_ex
    assert deck == deck_ex
