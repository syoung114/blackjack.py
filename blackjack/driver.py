import threading
import time
import random

from typing import Callable
from dataclasses import fields

from blackjack import rules, cards, io

from blackjack.state import FocusList, GameState, GameStage
from blackjack.rules import PayoutOrd
from blackjack.exception.StupidProgrammerException import StupidProgrammerException
from blackjack.strings.StringProvider import StringProvider

def make_deck_epoch():
    """
    Makes a 52 random deck seeded by epoch (POSIX time) in milliseconds.

    Impure, obviously
    """
    def _epoch_time_ms():
        return round(time.time() * 1000)

    epoch = _epoch_time_ms()
    seed = random.Random(epoch)
    return cards.make_deck_unordered(seed) 

def transition_logic(state : GameState, strings : StringProvider, reader : Callable[..., str], writer : Callable[[str], None]):
    """
    Given a GameStage and related state, returns the updated state according to blackjack logic and user input. Implemented as a state machine/pattern matching.

    Impure, but you can wrap it in a function that encapsulates state changes and returns a new GameState

    @arg state A GameState representing a snapshot of the working state
    """
    def ask_bet(bank) -> int:
        bet_constraint = io.Constraint().require(int).within(1, bank)
        bet = io.input_require(bet_constraint, strings.ask_bet(state), strings.ask_bet_fail(state), reader, writer)
        return bet

    def ask_hit() -> bool:
        return io.ask_binary(strings.input_hit(state), strings.input_stay(state), strings.ask_hit_stay(state), strings.ask_hit_stay_fail(state), reader, writer)

    def ask_want_split() -> bool:
        return io.ask_binary(strings.input_yes(state), strings.input_no(state), strings.ask_split(state), strings.ask_split_fail(state), reader, writer)

    def ask_want_insurance() -> bool:
        return io.ask_binary(strings.input_yes(state), strings.input_no(state), strings.ask_insurance(state), strings.ask_insurance_fail(state), reader, writer)

    match state.stage:
        case GameStage.ASK_BET:
            state.bet = ask_bet(state.bank)
            state.bank -= state.bet
            state.stage = GameStage.INIT_DEAL

        case GameStage.INIT_DEAL:
            # deal the player and dealer
            state.player = FocusList(rules.init_hand(state.deck))
            state.dealer = rules.init_hand(state.deck)

            writer(strings.show_player_hand(state))
            writer(strings.show_dealer_hand_down(state))

            # default case for if we don't automatically Stay because player holding natural
            state.stage = GameStage.ASK_INSURANCE

            if rules.is_natural(state.player[0]):
                state.stage = GameStage.PLAYER_DONE # still chance of a push when dealer plays
                # state.player.next()
                writer(strings.show_player_blackjack(state))

        case GameStage.ASK_INSURANCE:

            # default case for if we don't diverge because of successful insurance
            state.stage = GameStage.ASK_SPLIT

            # check and handle insurance
            # I'm partial to walrus operator but its lazy nature is very useful here.
            if (rules.is_insurable(state.dealer) and
                0 <= state.bank - (side_bet := rules.insurance_make_side_bet(state.bet)) and
                ask_want_insurance()):

                state.bank -= side_bet

                insurance_success, payout = rules.insure(
                    state.dealer,
                    side_bet
                )

                if insurance_success:
                    state.bank += payout
                    state.stage = GameStage.COMPLETE # this is intentionally not UPDATE_BANK. UPDATE_BANK compares player and dealer cards which insurance doesn't do.
                    writer(strings.show_insurance_success(state))
                else:
                    writer(strings.show_insurance_fail(state))

        case GameStage.ASK_SPLIT:
            if rules.can_split(state.player[0]) and ask_want_split():

                # that outer [0] is because [[[a]]] -> [[a]]. that third dimension is a symptom of what init_split returns. it's questionable to add a dependency of FocusList in that function.
                state.player = FocusList(rules.init_split(state.player[0], state.deck))[0]
                state.stage = GameStage.PLAYER_ACTIONS

                writer(strings.show_player_hand(state))

            else:
                state.stage=GameStage.PLAYER_ACTIONS

        case GameStage.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular isn't as true to the state machine model

            hand_completed = False

            # now ask to hit or stay and respond accordingly
            if ask_hit():
                cards.take_card(state.player.current(), state.deck)

                # compute hand value up front so the following two functions don't compute it twice
                hand_value = rules.hand_value(state.player.current())

                # busting won't happen on first deal but remember this state is for later hit/stay actions, unlike INIT_DEAL. 
                if rules.is_bust(hand_value):
                    writer(strings.show_bust(state.player.current()))
                    hand_completed = True

                elif rules.is_max(hand_value):
                    writer(strings.show_max_hand(state))
                    hand_completed = True

                else:
                    writer(strings.show_player_hand(state.player.current()))

            else:
                hand_completed = True

            if hand_completed:
                if state.player.has_next():
                    # increment the internal counter
                    state.player.next()
                else:
                    state.stage = GameStage.PLAYER_DONE

        case GameStage.PLAYER_DONE:
            rules.dealer_play(state.dealer, state.deck)
            state.stage = GameStage.UPDATE_BANK

            # if the dealer busted then report it.
            if rules.is_bust(state.dealer):
                writer(strings.show_bust(state.dealer))
            else:
                writer(strings.show_dealer_hand_up(state))

        case GameStage.UPDATE_BANK:

            # winning logic specifically for naturals has not yet been applied. When we transitioned from a blackjack, the code didn't compute winnings. We now compute winnings.
            if len(state.player) == 1 and rules.is_natural(state.player[0]):
                # importantly notice that state.player[0]. Easy to miss if refactoring.
                state.bank += rules.bet_hand(state.player[0], state.dealer, state.bet, win_odds=PayoutOrd.THREE_TWO)

            else:
                state.bank += rules.winnings(state.player, state.dealer, state.bet)

            state.stage = GameStage.COMPLETE
            writer(strings.show_bank(state))

        case GameStage.COMPLETE:

            # tear down the state so that we can notice unexpected behavior with None if we start over
            for field in fields(state):
                # the attributes in the list are those allowed to persist between rounds
                if field.name not in ['bank', 'deck']:
                    setattr(state, str(field), None)

            state.stage = GameStage.ASK_BET

        case _:
            raise StupidProgrammerException(f"missed case {state.stage} in driver.transition_logic")

def driver_io(
    ext_stop_pred : threading.Event,
    strings : StringProvider,
    reader : Callable[..., str] = input,
    writer : Callable[[str], None] = print
):
    """
    Sort of like main() or a rules.loop. It's the highest level driver of program logic and it creates the I/O side effects concerning user input and display.
    """
    try:
        def ask_bank() -> int:
            constraint = io.Constraint().require(int).at_least(1)
            return io.input_require(constraint, strings.ask_bank(), strings.ask_bank_fail(), reader, writer)
        init_state = GameState(GameStage.ASK_BET, make_deck_epoch(), ask_bank(), None, None, None)

        while not ext_stop_pred.is_set():
            if len(init_state.deck) <= 13: # this is arbitrary for the moment while other details are realized.
                init_state.deck = make_deck_epoch()
                writer(strings.show_shuffling(init_state))
            writer(str(init_state.stage))
            transition_logic(init_state, strings, reader, writer)

    except KeyboardInterrupt:
        writer(strings.show_keyboard_interrupt(init_state))
