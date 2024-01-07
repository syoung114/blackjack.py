import pytest

import blackjack.constants as constants
import blackjack.cards as cards
import tests.fixtures_cards as fixtures_cards

@pytest.mark.parametrize("ex", [
    ("fix_deck_alphabetical_52")
])
def test_make_deck_ordered(request, ex):
    assert cards.make_deck_ordered() == ex

@pytest.mark.parametrize("seed,ex", [
    ("fix_rseed_zero", "fix_deck_rseed_zero")
])
def test_make_deck_unordered_alt(request, seed, ex):
    assert cards.make_deck_unordered(seed) == ex and len(cards.Rank) * len(cards.Suit) == constants.DECK_SIZE

@pytest.mark.parametrize("seed,ex", [
    ("fix_deck_alphabetical_52", "fix_deck_rseed_zero")
])
def test_make_deck_unordered2(request, seed, ex):
    ord_deck = cards.make_deck_ordered()
    seed.shuffle(ord_deck)
    assert ord_deck == ex

@pytest.mark.parametrize("a,b,ex", [
    (1, 0, cards.Ordinal.GT),
    (0, 0, cards.Ordinal.EQ),
    (0, 1, cards.Ordinal.LT)
])
def test_compare(request, a, b, ex):
    # note I know about comparing floating points but using floating point numbers in this module aren't our intention
    assert cards.compare(a,b) == ex

@pytest.mark.parametrize("raw,ex", [
    ("fix_hand_one_card_raw", "fix_hand_one_card_tups"),
    ("fix_hand_pair_identical_raw", "fix_hand_pair_identical_tups"), # In blackjack this is illegal but I believe defining such logic is curiously outside the scope of the function.
    ("fix_hand_different_suit_raw", "fix_hand_different_suit_tups"),
    ("fix_hand_pair_equal_low_raw", "fix_hand_pair_equal_low_tups"),
    ("fix_hand_alphabetical_52_raw", "fix_deck_alpabetical_52"),
    ("fix_hand_valid_interleaved", "fix_hand_one_card_tups"),
    ("fix_hand_invalid_interleaved", "fix_deck_empty_tup"),
    ("fix_hand_junk", "fix_hand_empty_tup"),
    ("fix_hand_empty_raw", "fix_hand_empty_tup"),
    ("fix_hand_empty_invalid_interleaved", "fix_hand_empty_tup"),
])
def test_parse_hand(request, raw, ex):
    # a lot of tests depend on this function (because manually defining a card through tuple is PITA) so it's important to get right.
    return cards.parse_hand(raw) == ex

@pytest.mark.parametrize("h1,h2,ex", [
    ("fix_hand_one_card_tups", "fix_hand_one_card_tups", cards.Ordinal.EQ),
    ("fix_hand_pair_equal_low_tups", "fix_hand_one_card_tups", cards.Ordinal.GT),
    ("fix_hand_one_card_tups", "fix_hand_pair_equal_low_tups", cards.Ordinal.LT)
])
def test_compare_hand(request, h1, h2, ex):
    assert cards.compare_hand(h1,h2) == ex

@pytest.mark.parametrize("hand,deck,hex,dex", [
    ([], "fix_hand_one_card_tups", "fix_hand_one_card_tups", []),
    ([], "fix_hand_pair_different_tups", "fix_hand_one_card_tups", cards.parse_hand("AD")),
    ("fix_hand_one_card_tups", cards.parse_hand("AD"), "fix_hand_pair_different_tups", [])
    # there's also taking from an empty deck but I prefer to leave that as undefined behavior.
])
def test_take_card(request, hand, deck, hex, dex):
    assert hand == hex
    assert deck == dex

