import threading
import time
import random

from typing import Callable
from dataclasses import fields

from blackjack.core import constants, rules, cards
from blackjack.core.PayoutOdds import PayoutOdds

from blackjack.core.exception.StupidProgrammerException import StupidProgrammerException

from blackjack.core.io.InputProvider import InputProvider
from blackjack.core.io.OutputProvider import OutputProvider

from blackjack.core.state import GameState, GameStage, PlayerAction

def transition_logic(state : GameState, inputs : InputProvider, strings : OutputProvider, reader : Callable[..., str], writer : Callable[[str], None]):
    """
    Given a GameStage and related state, returns the updated state according to blackjack logic and user input. Implemented as a state machine/pattern matching.

    Impure, but you can wrap it in a function that encapsulates state changes and returns a new GameState

    @arg state A GameState representing a snapshot of the working state
    """
    match state.stage:
        case GameStage.ASK_BET:
            state.bet = inputs.input_bet(state, reader, writer)
            state.bank -= state.bet
            state.stage = GameStage.INIT_DEAL

        case GameStage.INIT_DEAL:
            # deal the player and dealer
            state.player = [rules.init_hand(state.deck)]
            state.current_hand = 0
            state.dealer = rules.init_hand(state.deck)
            state.stage = GameStage.ASK_INSURANCE

            strings.show_player_hand(state, writer)
            strings.show_dealer_hand_down(state, writer)

        case GameStage.ASK_INSURANCE:

            # default case for if we don't diverge because of insurance or blackjacks
            state.stage = GameStage.ASK_SPLIT

            # check and handle insurance
            # I'm partial to walrus operator but its lazy nature is very useful here.
            if (rules.is_insurable(state.dealer) and
                0 <= state.bank - (side_bet := rules.insurance_make_side_bet(state.bet)) and
                inputs.input_want_insurance(state, reader, writer)):

                state.bank -= side_bet

                insurance_success, win_payout = rules.insure(
                    state.dealer,
                    side_bet
                )

                if insurance_success:
                    state.bank += win_payout
                    strings.show_insurance_success(state, writer)
                else:
                    strings.show_insurance_fail(state, writer)

            if rules.is_natural(state.player[state.current_hand]):
                state.stage = GameStage.PLAYER_DONE
                state.current_hand += 1

        case GameStage.ASK_SPLIT:
            # note that although I put state.current_hand in the following, it means zero. It's for consistency and development flexibility.
            if (rules.can_split(state.player[state.current_hand]) and
                state.bank - state.bet >= 0 and
                inputs.input_want_split(state, reader, writer)):

                # rules.init_split :: [[Hand]] -> [[Hand], [Hand]]
                # because 0 -> 0 state.current_hand doesn't change
                state.player = rules.init_split(state.player[state.current_hand], state.deck)

                state.stage = GameStage.PLAYER_ACTIONS
                state.bank -= state.bet
                state.bet *= 2

                strings.show_player_hand(state, writer)

            else:
                state.stage=GameStage.PLAYER_ACTIONS

        case GameStage.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular isn't as true to the state machine model

            # for control flow of stays and busts
            hand_completed = False

            # player decision. Using None because we can tell quickly when something's wrong
            hit_stay_double = None

            # check if double is possible by asking if initial hand (also sufficient funds to make the double)
            if len(state.player[state.current_hand]) == constants.INITIAL_HAND_LEN and state.bank - state.bet >= 0:

                hit_stay_double = inputs.input_hit_stay_double(state, reader, writer)
                if hit_stay_double == PlayerAction.DOUBLE:
                    state.bank -= state.bet
                    state.bet *= 2
                    hand_completed = True

            # this hand isn't initial
            else:
                hit_stay_double = inputs.input_hit(state, reader, writer)

            # handle hits and doubles.
            # in the case of doubles, the following logic is the same but hand_completed is overridden to be True, because the next card is their last regardless of result.
            if hit_stay_double == PlayerAction.HIT or hit_stay_double == PlayerAction.DOUBLE:
                cards.take_card(state.player[state.current_hand], state.deck)

                # compute hand value up front so the following two functions don't compute it twice
                hand_value = rules.hand_value(state.player[state.current_hand])

                # busting won't happen on first deal but remember this state is for later hit/stay actions, unlike INIT_DEAL. 
                if rules.is_bust(hand_value):
                    strings.show_player_bust(state, writer)
                    hand_completed = True

                elif rules.is_max(hand_value):
                    strings.show_max_hand(state, writer)
                    hand_completed = True

                else:
                    strings.show_player_hand(state, writer)

            elif hit_stay_double == PlayerAction.STAY:
                hand_completed = True

            else:
                raise StupidProgrammerException("missed hit/stay/double implementation")

            if hand_completed:
                state.current_hand += 1
                if len(state.player) == state.current_hand:
                    state.stage = GameStage.PLAYER_DONE

        case GameStage.PLAYER_DONE:
            rules.dealer_play(state.dealer, state.deck)
            state.stage = GameStage.UPDATE_BANK

            # if the dealer busted then report it.
            if rules.is_bust(state.dealer):
                strings.show_dealer_bust(state, writer)
            else:
                strings.show_dealer_hand_up(state, writer)

        case GameStage.UPDATE_BANK:

            # winning logic specifically for naturals has not yet been applied. When we transitioned from a blackjack, the code didn't compute winnings. We now compute winnings.
            if len(state.player) == 1 and rules.is_natural(state.player[0]):
                # importantly notice that state.player[0]. Easy to miss if refactoring.
                state.bank += rules.bet_hand(state.player[0], state.dealer, state.bet, win_odds=PayoutOdds.THREE_TWO)

            else:
                state.bank += rules.winnings(state.player, state.dealer, state.bet)

            state.bet = 0
            state.stage = GameStage.COMPLETE
            strings.show_bank(state, writer)

        case GameStage.COMPLETE:

            # tear down the state so that we can notice unexpected behavior with None if we start over
            for field in fields(state):
                # the attributes in the list are those allowed to persist between rounds
                if field.name not in ['bank', 'deck']:
                    setattr(state, str(field.name), None)

            state.stage = GameStage.ASK_BET

        case _:
            raise StupidProgrammerException(f"missed case {state.stage} in driver.transition_logic")

def driver_io(
    ext_stop_pred : threading.Event,
    inputs : InputProvider,
    strings : OutputProvider,
    reader : Callable[..., str]=input,
    writer : Callable[[str], None]=print,
):
    """
    Sort of like main() or a rules.loop. It's the highest level driver of program logic and it creates the I/O side effects concerning user input and display.
    """

    def make_deck_epoch():
        def _epoch_time_ms():
            return round(time.time() * 1000)
    
        epoch = _epoch_time_ms()
        seed = random.Random(epoch)
        return cards.make_deck_unordered(seed) 

    try:
        state = GameState(GameStage.ASK_BET, make_deck_epoch(), inputs.input_bank(reader, writer), None, None, None, None)
        completed_rounds = 0

        while not ext_stop_pred.is_set():
            if state.stage == GameStage.COMPLETE: 
                completed_rounds += 1

            if completed_rounds >= 3: # I know this is magic number. don't care for now.
                completed_rounds = 0
                state.deck = make_deck_epoch()

                strings.show_shuffling(state, writer)
            #writer(str(state.stage))

            transition_logic(state, inputs, strings, reader, writer)

    except KeyboardInterrupt:
        strings.show_keyboard_interrupt(state, writer)
