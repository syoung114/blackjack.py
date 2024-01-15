"""
Unit testing GameState mutations per GameStage. Assumes correct user input.
"""
import pytest

from copy import deepcopy

from blackjack import driver
from blackjack.state import GameStage, GameState
from blackjack.cards import parse_hand

from tests.test_io import PrintMock, InputMock, print_stub
from tests.fixtures_cards import fix_deck_alphabetical_52
from tests.TestStrings import TestStrings
from tests import helper_hands

def test_transition_logic_ASK_BET(fix_deck_alphabetical_52):

    state_in = GameState(GameStage.ASK_BET, fix_deck_alphabetical_52, 100, None, None, None, None)
    state_ex = GameState(GameStage.INIT_DEAL, fix_deck_alphabetical_52, 90, 10, None, None, None)

    input_mock = InputMock(["10"])

    driver.transition_logic(state_in, TestStrings(), input_mock.input, print_stub)

    assert state_in == state_ex




def test_transition_logic_INIT_DEAL_non_natural(fix_deck_alphabetical_52):

    original_deck = deepcopy(fix_deck_alphabetical_52)

    state_in = GameState(GameStage.INIT_DEAL, fix_deck_alphabetical_52, 90, 10, None, None, None)
    state_ex = GameState(GameStage.ASK_INSURANCE, original_deck[:-4], 90, 10, [parse_hand("KSQS")], 0, parse_hand("JS10S"))

    input_mock = InputMock([])
    driver.transition_logic(state_in, TestStrings(), input_mock.input, print_stub)

    assert state_in == state_ex

def test_transition_logic_INIT_DEAL_natural():
    # also see the integration test which this test redundantly covers the first half of

    # note this test carries another assumption that the deck size can go this low in size.
    state_in = GameState(GameStage.INIT_DEAL, parse_hand("KSQSJSAH"), 90, 10, None, None, None)
    state_ex = GameState(GameStage.PLAYER_DONE, [], 90, 10, [parse_hand("AHJS")], 1, parse_hand("QSKS"))

    input_mock = InputMock([])
    driver.transition_logic(state_in, TestStrings(), input_mock.input, print_stub)

    assert state_in == state_ex




@pytest.mark.parametrize("state_in,state_ex,input_mock", [
    # note that the player hand and deck are None because we don't care about their state in this test. If the original code tried to modify either, the test would likely fail, as it should. Anyway, their implementation doesn't matter in unit testing as long as they pass the tests, so I like the idea of None effectively encapsulating that.
    (
        # not insurable
        GameState(GameStage.ASK_INSURANCE, None, 90, 10, None, None, parse_hand("2H2S")),
        GameState(GameStage.ASK_SPLIT, None, 90, 10, None, None, parse_hand("2H2S")),
        InputMock([]), # we are also testing if the input didn't prompt here. We can't take from empty queue.
    ),
    (
        # face down ace (even if it's actually blackjack). should be identical path to previous test.
        GameState(GameStage.ASK_INSURANCE, None, 90, 10, None, None, helper_hands.hand_blackjack_ace_down()),
        GameState(GameStage.ASK_SPLIT, None, 90, 10, None, None, helper_hands.hand_blackjack_ace_down()),
        InputMock([]), # we are also testing if the input didn't prompt here. We can't take from empty queue.
    ),
    (
        # Insufficient funds. In insurance this would result from the player going all in.
        # this test ensures they aren't prompted for insurance at $0
        GameState(GameStage.ASK_INSURANCE, None, 0, 10, None, None, helper_hands.hand_blackjack_ace_up()),
        GameState(GameStage.ASK_SPLIT, None, 0, 10, None, None, helper_hands.hand_blackjack_ace_up()),
        InputMock([]), # we are also testing if the input didn't prompt here. We can't take from empty queue.
    ),
    (
        # insurable (and it *is* blackjack) but player doesn't want it (they can't see that it's blackjack)
        GameState(GameStage.ASK_INSURANCE, None, 90, 10, None, None, helper_hands.hand_blackjack_ace_up()),
        GameState(GameStage.ASK_SPLIT, None, 90, 10, None, None, helper_hands.hand_blackjack_ace_up()),
        InputMock(["no"]),
    ),
    (
        # insurance fails. see https://boardgames.stackexchange.com/a/27182
        # see also integration test where player loses insurance and plays on
        GameState(GameStage.ASK_INSURANCE, None, 800, 200, None, None, parse_hand("AS2S")),
        GameState(GameStage.ASK_SPLIT, None, 700, 200, None, None, parse_hand("AS2S")),
        InputMock(["yes"]),
    ),
    (
        # insurance succeeds. see https://boardgames.stackexchange.com/a/27182
        # the bet persisting is intentional.
        GameState(GameStage.ASK_INSURANCE, None, 800, 200, None, None, helper_hands.hand_blackjack_ace_up()),
        GameState(GameStage.COMPLETE, None, 1000, 200, None, None, helper_hands.hand_blackjack_ace_up()),
        InputMock(["yes"]),
    )
])
def test_transition_logic_ASK_INSURANCE(state_in, state_ex, input_mock):
    driver.transition_logic(state_in, TestStrings(), input_mock.input, print_stub)
    assert state_in == state_ex
    assert input_mock.empty()



@pytest.mark.parametrize("state_in,state_ex,input_mock", [
    (
        # can't split
        GameState(GameStage.ASK_SPLIT, None, None, None, [helper_hands.hand_blackjack_ace_up()], 0, None),
        GameState(GameStage.PLAYER_ACTIONS, None, None, None, [helper_hands.hand_blackjack_ace_up()], 0, None),
        InputMock([])
    ),
    (
        # can split but insufficient funds
        GameState(GameStage.ASK_SPLIT, None, 0, 100, [helper_hands.hand_2C2D()], 0, None),
        GameState(GameStage.PLAYER_ACTIONS, None, 0, 100, [helper_hands.hand_2C2D()], 0, None),
        InputMock([])
    ),
    (
        # can split but player declines
        GameState(GameStage.ASK_SPLIT, None, 100, 10, [helper_hands.hand_2C2D()], 0, None),
        GameState(GameStage.PLAYER_ACTIONS, None, 100, 10, [helper_hands.hand_2C2D()], 0, None),
        InputMock(["no"])
    ),
    (
        # can split and player accepts
        GameState(GameStage.ASK_SPLIT, parse_hand("3C3D"), 100, 10, [helper_hands.hand_2C2D()], 0, None),
        GameState(GameStage.PLAYER_ACTIONS, [], 90, 20, [parse_hand("2C3D"), parse_hand("2D3C")], 0, None),
        InputMock(["yes"])
    ),

])
def test_transition_logic_ASK_SPLIT(state_in,state_ex,input_mock):
    driver.transition_logic(state_in, TestStrings(), input_mock.input, print_stub)
    assert state_in == state_ex
    assert input_mock.empty()




@pytest.mark.parametrize("state_in,state_ex", [
    (
        # Player hits single hand and busts
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("KC"), None, None, [helper_hands.hand_17_len_3()], 0, None),
        GameState(GameStage.PLAYER_DONE, [], None, None, [helper_hands.hand_17_len_3() + parse_hand("KC")], 1, None),
    ),
    (
        # 21 after hit
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("AD"), None, None, [parse_hand("4C5CAC")], 0, None),
        GameState(GameStage.PLAYER_DONE, [], None, None, [parse_hand("4C5CACAD")], 1, None),
    ),
    (
        # neither above.
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("3C"), None, None, [helper_hands.hand_17_len_3()], 0, None),
        GameState(GameStage.PLAYER_ACTIONS, [], None, None, [helper_hands.hand_17_len_3() + parse_hand("3C")], 0, None)
    )
])
def test_transition_logic_PLAYER_ACTIONS_single_hit(state_in,state_ex):
    mock_input = InputMock(["hit"])
    driver.transition_logic(state_in, TestStrings(), mock_input.input, print_stub)
    assert state_in == state_ex
    assert mock_input.empty()








@pytest.mark.parametrize("state_in,state_ex", [
    (
        # Player hits single hand and busts
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("KC"), 400, 100, [helper_hands.hand_17_len_2()], 0, None),
        GameState(GameStage.PLAYER_DONE, [], 300, 200, [helper_hands.hand_17_len_2() + parse_hand("KC")], 1, None),
    ),
    (
        # 21 after hit
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("AD"), 400, 100, [parse_hand("5D5C")], 0, None),
        GameState(GameStage.PLAYER_DONE, [], 300, 200, [parse_hand("5D5CAD")], 1, None),
    ),
    (
        # neither above.
        GameState(GameStage.PLAYER_ACTIONS, parse_hand("3C"), 400, 100, [helper_hands.hand_17_len_2()], 0, None),
        GameState(GameStage.PLAYER_DONE, [], 300, 200, [helper_hands.hand_17_len_2() + parse_hand("3C")], 1, None)
    )
])
def test_transition_logic_PLAYER_ACTIONS_single_double(state_in,state_ex):
    mock_input = InputMock(["double"])
    driver.transition_logic(state_in, TestStrings(), mock_input.input, print_stub)
    assert state_in == state_ex
    assert mock_input.empty()




def test_transition_logic_PLAYER_ACTIONS_single_stay():
    state_in = GameState(GameStage.PLAYER_ACTIONS, None, None, None, [helper_hands.hand_17_len_3()], 0, None)
    state_out = GameState(GameStage.PLAYER_DONE, None, None, None, [helper_hands.hand_17_len_3()], 1, None)

    driver.transition_logic(state_in, TestStrings(), InputMock(["stay"]).input, print_stub)

    assert state_in == state_out


def test_transition_logic_PLAYER_DONE(fix_deck_alphabetical_52):

    original_deck_len = len(fix_deck_alphabetical_52) # I know the length is in the identifier but that's technically a magic number

    state_in = GameState(GameStage.PLAYER_DONE, fix_deck_alphabetical_52, None, None, None, None, helper_hands.hand_2C2D())

    driver.transition_logic(state_in, TestStrings(), InputMock([]), print_stub)

    assert state_in.stage == GameStage.UPDATE_BANK

    # we just want to acknowledge that some transformation happened here. the details are a lower level of testing (which we've already covered)..
    assert original_deck_len > len(fix_deck_alphabetical_52)
    assert state_in.dealer != helper_hands.hand_2C2D()




@pytest.mark.parametrize("state_in,state_ex", [
    (
        # natural winning blackjack. also covered in integration tests.
        GameState(GameStage.UPDATE_BANK, None, 100, 100, [helper_hands.hand_blackjack_ace_up()], 1, helper_hands.hand_17_len_2()),
        GameState(GameStage.COMPLETE, None, 350, 0, [helper_hands.hand_blackjack_ace_up()], 1, helper_hands.hand_17_len_2()),
    ),
    (
        # natural pushing blackjack. also covered in integration tests.
        GameState(GameStage.UPDATE_BANK, None, 100, 100, [helper_hands.hand_blackjack_ace_up()], 1, helper_hands.hand_blackjack_ace_down()),
        GameState(GameStage.COMPLETE, None, 200, 0, [helper_hands.hand_blackjack_ace_up()], 1, helper_hands.hand_blackjack_ace_down()),
    ),
    (
        # 21 (non natural) vs 20
        GameState(GameStage.UPDATE_BANK, None, 100, 100, [parse_hand("10C QD AS")], 1, parse_hand("JD KD")),
        GameState(GameStage.COMPLETE, None, 300, 0, [parse_hand("10C QD AS")], 1, parse_hand("JD KD")),
    ),
    (
        # one hand, length 2, winning, but not 21
        GameState(GameStage.UPDATE_BANK, None, 100, 100, [helper_hands.hand_18_len_2()], 1, helper_hands.hand_17_len_2()),
        GameState(GameStage.COMPLETE, None, 300, 0, [helper_hands.hand_18_len_2()], 1, helper_hands.hand_17_len_2()),
    ),
    (
        # two hands, both win, see also test_rules.test_winnings
        GameState(GameStage.UPDATE_BANK, None, 0, 200, [helper_hands.hand_18_len_3(), helper_hands.hand_18_len_2()], 2, helper_hands.hand_17_len_3()),
        GameState(GameStage.COMPLETE, None, 400, 0, [helper_hands.hand_18_len_3(), helper_hands.hand_18_len_2()], 2, helper_hands.hand_17_len_3()),
    ),
    (
        # two hands, one win, one push. see also test_rules.test_winnings
        GameState(GameStage.UPDATE_BANK, None, 0, 200, [helper_hands.hand_18_len_3(), helper_hands.hand_17_len_2()], 2, helper_hands.hand_17_len_3()),
        GameState(GameStage.COMPLETE, None, 300, 0, [helper_hands.hand_18_len_3(), helper_hands.hand_17_len_2()], 2, helper_hands.hand_17_len_3()),
    ),
    (
        # two hands, one win, one loss. see also test_rules.test_winnings
        GameState(GameStage.UPDATE_BANK, None, 0, 200, [helper_hands.hand_18_len_3(), helper_hands.hand_2C2D()], 2, helper_hands.hand_17_len_3()),
        GameState(GameStage.COMPLETE, None, 200, 0, [helper_hands.hand_18_len_3(), helper_hands.hand_2C2D()], 2, helper_hands.hand_17_len_3()),
    ),
    (
        # two hands, both loss. see also test_rules.test_winnings
        GameState(GameStage.UPDATE_BANK, None, 0, 200, [helper_hands.hand_18_len_3(), helper_hands.hand_2C2D()], 2, helper_hands.hand_blackjack_ace_down()),
        GameState(GameStage.COMPLETE, None, 0, 0, [helper_hands.hand_18_len_3(), helper_hands.hand_2C2D()], 2, helper_hands.hand_blackjack_ace_down()),
    ),
])
def test_transition_logic_UPDATE_BANK(state_in,state_ex):
    input_mock = InputMock([])
    driver.transition_logic(state_in,TestStrings(),input_mock.input,print_stub)
    assert state_in==state_ex
    assert input_mock.empty()




def test_transition_logic_COMPLETE(fix_deck_alphabetical_52):

    # simulate some cards been removed from the deck
    used_deck = fix_deck_alphabetical_52[:42]

    state_in = GameState(GameStage.COMPLETE, used_deck, 456, 123, [helper_hands.hand_18_len_3()], 1, helper_hands.hand_17_len_2())
    state_ex = GameState(GameStage.ASK_BET, used_deck, 456, None, None, None, None)

    driver.transition_logic(state_in, TestStrings(), InputMock([]), print_stub)

    assert state_in == state_ex
