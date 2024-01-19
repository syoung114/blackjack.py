from blackjack.core.cards import parse_hand
from blackjack.core.driver import transition_logic
from blackjack.core.state import GameStage, GameState
from tests.core import helper_hands

from tests.core.TestStrings import TestStrings
from tests.core.mocks_io import InputMock, print_stub
from tests.core.test_io import InputRequireString

#########

def test_happy_path():
    deck_in = parse_hand("5C6H5H8S2S5H7C5D")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100", "hit", "stay"])

    # ask bet
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)

    # init deal
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("5C6H5H8S"), 100, 100, [parse_hand("5D7C")], 0, parse_hand("5H2S"))

    # ask insurance (skips)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_SPLIT, parse_hand("5C6H5H8S"), 100, 100, [parse_hand("5D7C")], 0, parse_hand("5H2S"))

    # ask split (skips)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("5C6H5H8S"), 100, 100, [parse_hand("5D7C")], 0, parse_hand("5H2S"))

    # player actions (player hits)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("5C6H5H"), 100, 100, [parse_hand("5D7C8S")], 0, parse_hand("5H2S"))

    # player actions (player stays)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_DONE, parse_hand("5C6H5H"), 100, 100, [parse_hand("5D7C8S")], 1, parse_hand("5H2S"))

    # all inputs should be consumed by this point
    assert input_mock.empty()

    # dealer plays (this is one-shot stage)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.UPDATE_BANK, parse_hand("5C"), 100, 100, [parse_hand("5D7C8S")], 1, parse_hand("5H2S5H6H"))

    # update bank (20 > 18, so player win)
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.COMPLETE, parse_hand("5C"), 300, 0, [parse_hand("5D7C8S")], 1, parse_hand("5H2S5H6H"))

    # complete. notice we now can cycle back to the start.
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_BET, parse_hand("5C"), 300, None, None, None, None)




def test_split_happy():
    deck_in = parse_hand("2H5C3C2CKS4C5D8C10DAHAS")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100", "yes", "hit", "hit", "hit", "hit", "stay"])

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("2H5C3C2CKS4C5D"), 100, 100, [parse_hand("ASAH")], 0, parse_hand("10D8C"))

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_SPLIT, parse_hand("2H5C3C2CKS4C5D"), 100, 100, [parse_hand("ASAH")], 0, parse_hand("10D8C"))

    # "yes" consumed here. this is where the split actually happens
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("2H5C3C2CKS"), 0, 200, [parse_hand("AS5D"), parse_hand("AH4C")], 0, parse_hand("10D8C"))

    # hand 1, initial, value 16 (soft), choose hit
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("2H5C3C2C"), 0, 200, [parse_hand("AS5DKS"), parse_hand("AH4C")], 0, parse_hand("10D8C"))

    # hand 1, initial, value 16 (hard), choose hit
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("2H5C3C"), 0, 200, [parse_hand("AS5DKS2C"), parse_hand("AH4C")], 0, parse_hand("10D8C"))

    # hand 1, second choice, value 18, choose hit
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("2H5C"), 0, 200, [parse_hand("AS5DKS2C3C"), parse_hand("AH4C")], 1, parse_hand("10D8C"))

    # hand 2, value 15 (prev hand 21), choose hit
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_ACTIONS, parse_hand("2H"), 0, 200, [parse_hand("AS5DKS2C3C"), parse_hand("AH4C5C")], 1, parse_hand("10D8C"))

    # hand 2, val 20, choose stay.
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_DONE, parse_hand("2H"), 0, 200, [parse_hand("AS5DKS2C3C"), parse_hand("AH4C5C")], 2, parse_hand("10D8C"))

    assert input_mock.empty()

    # dealer does nothing here because >= 17
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.UPDATE_BANK, parse_hand("2H"), 0, 200, [parse_hand("AS5DKS2C3C"), parse_hand("AH4C5C")], 2, parse_hand("10D8C"))

    # update bank
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.COMPLETE, parse_hand("2H"), 400, 0, [parse_hand("AS5DKS2C3C"), parse_hand("AH4C5C")], 2, parse_hand("10D8C"))

    # complete
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_BET, parse_hand("2H"), 400, None, None, None, None)








def test_blackjack_win():
    """
    blackjack (win) flow from the beginning
    """

    deck_in = parse_hand("KS2C6S10HAD10C")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100"])
    
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)
    assert input_mock.empty()

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("KS2C"), 100, 100, [parse_hand("10CAD")], 0, parse_hand("10H6S"))

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_DONE, parse_hand("KS2C"), 100, 100, [parse_hand("10CAD")], 1, parse_hand("10H6S"))

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.UPDATE_BANK, parse_hand("KS"), 100, 100, [parse_hand("10CAD")], 1, parse_hand("10H6S2C"))

    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.COMPLETE, parse_hand("KS"), 350, 0, [parse_hand("10CAD")], 1, parse_hand("10H6S2C"))




def test_blackjack_push():
    """
    blackjack (push) flow from the beginning. ace is down so no insurance.
    """

    deck_in = parse_hand("KS2CAS10HAD10C")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100"])
    
    # ask bet
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)
    assert input_mock.empty()

    # init deal
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("KS2C"), 100, 100, [parse_hand("10CAD")], 0, parse_hand("10HAS"))

    # ask about insurance. because ace down, no insurance.
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.PLAYER_DONE, parse_hand("KS2C"), 100, 100, [parse_hand("10CAD")], 1, parse_hand("10HAS"))

    # player done
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.UPDATE_BANK, parse_hand("KS2C"), 100, 100, [parse_hand("10CAD")], 1, parse_hand("10HAS"))

    # update bank
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.COMPLETE, parse_hand("KS2C"), 200, 0, [parse_hand("10CAD")], 1, parse_hand("10HAS"))

    # complete
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_BET, parse_hand("KS2C"), 200, None, None, None, None) 






def test_insurance_win():
    """
    winning insurance flow
    """
    deck_in = parse_hand("2HKDAC2D2C")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100", "yes"])
    
    # ask bet
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)

    # init deal
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("2H"), 100, 100, [parse_hand("2C2D")], 0, parse_hand("ACKD"))

    # ask insurance
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_SPLIT, parse_hand("2H"), 200, 100, [parse_hand("2C2D")], 0, parse_hand("ACKD"))

    # game continues along happy path




def test_insurance_loss():
    deck_in = parse_hand("2H9DAC2D2C")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100", "yes"])
    
    # ask bet
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)

    # init deal
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("2H"), 100, 100, [parse_hand("2C2D")], 0, parse_hand("AC9D"))

    # ask insurance
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_SPLIT, parse_hand("2H"), 50, 100, [parse_hand("2C2D")], 0, parse_hand("AC9D"))




def test_insurance_decline():
    """
    winning insurance flow
    """
    deck_in = parse_hand("2HKDAC2D2C")
    state_in = GameState(GameStage.ASK_BET, deck_in, 200, None, None, None, None)

    input_mock = InputMock(["100", "no"])
    
    # ask bet
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.INIT_DEAL, deck_in, 100, 100, None, None, None)

    # init deal
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_INSURANCE, parse_hand("2H"), 100, 100, [parse_hand("2C2D")], 0, parse_hand("ACKD"))

    # ask insurance
    transition_logic(state_in, TestStrings, input_mock.input, print_stub)
    assert state_in == GameState(GameStage.ASK_SPLIT, parse_hand("2H"), 100, 100, [parse_hand("2C2D")], 0, parse_hand("ACKD"))
