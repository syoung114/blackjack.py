import threading
import time
import random

from typing import Callable
from dataclasses import fields

from blackjack import rules, cards, io

from blackjack.state import GameState, GameStage
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

    def handle_init_hand():
        state.player = rules.init_hand(state.deck)
        state.dealer = rules.init_hand(state.deck)
        writer(strings.show_player_hand(state))
        writer(strings.show_dealer_hand_down(state))

    match state.stage:
        case GameStage.ASK_BET:
            state.bet = ask_bet(state.bank)

            # in blackjack we take away the bet and the player either wins it back (maybe then some) or they don't get anything.
            state.bank -= state.bet

            state.stage = GameStage.INIT_DEAL

        case GameStage.INIT_DEAL:
            # deal the player and dealer. modifies the deck via side effect in the process.
            handle_init_hand()

            # default case for if we don't automatically Stay because player holding natural
            state.stage = GameStage.ASK_INSURANCE

            if rules.is_natural(state.player):
                writer(strings.show_player_blackjack(state))

                state.player_completed = [state.player]
                state.player = []
                state.stage = GameStage.PLAYER_DONE # still chance of a push when dealer plays

        case GameStage.ASK_INSURANCE:

            # default case for if we don't diverge because of successful insurance
            state.stage = GameStage.ASK_SPLIT

            # check and handle insurance
            if rules.is_insurable(state.dealer) and ask_want_insurance():

                side_bet = rules.insurance_make_side_bet(state.bet)
                state.bank -= side_bet

                insurance_success, payout = rules.insure(
                    state.dealer,
                    side_bet
                )

                # side_bet_payout is negative for lost bet.
                state.bank += payout

                if insurance_success:
                    writer(strings.show_insurance_success(state))
                    state.stage = GameStage.COMPLETE # this is intentionally not UPDATE_BANK. UPDATE_BANK compares cards which insurance doesn't do.
                else:
                    writer(strings.show_insurance_fail(state))

        case GameStage.ASK_SPLIT:
            if rules.can_split(state.player) and ask_want_split():

                state.player = rules.init_split(state.player, state.deck)
                state.stage = GameStage.PLAYER_ACTIONS

                writer(strings.show_player_hand(state))

            else:
                state.stage=GameStage.PLAYER_ACTIONS

        case GameStage.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular isn't as true to the state machine model

            is_split = isinstance(state.player[0],list)
            hand_completed = False
            current_hand = None

            if is_split:
                # using the last hand because it grants an O(1) removal with .pop(). see the hand_completed block for that.
                # before you say "use state.player[:-1]", that's not O(1), amusingly.
                current_hand = state.player[len(state.player) - 1]
            else:
                current_hand = state.player

            # now ask to hit or stay and respond accordingly
            if ask_hit():
                cards.take_card(current_hand, state.deck)

                # compute hand value up front so the following two functions don't compute it twice
                hand_value = rules.hand_value(current_hand)

                # busting won't happen on first deal but remember this state is for later hit/stay actions, unlike INIT_DEAL. 
                if rules.is_bust(hand_value):
                    writer(strings.show_bust(current_hand))
                    hand_completed = True

                elif rules.is_max(hand_value):
                    writer(strings.show_max_hand(state))
                    hand_completed = True

                else:
                    writer(strings.show_player_hand(current_hand))

            else:
                hand_completed = True

            if hand_completed:
                # Because splits and hands aren't equal representations we must handle inserting them differently into the player_completed list.

                # Up to this point player_completed has potentially not been used.
                if state.player_completed == None:
                    state.player_completed = []

                if is_split:
                    state.player_completed.append(state.player.pop())

                else:
                    # state.player.pop() doesn't work because that removes a single card
                    state.player_completed.append(state.player)
                    state.player = []

                if len(state.player) == 0:
                    state.stage = GameStage.PLAYER_DONE


        case GameStage.PLAYER_DONE:
            rules.dealer_play(state.dealer, state.deck)

            # if the dealer busted then report it.
            if rules.is_bust(state.dealer):
                writer(strings.show_bust(state.dealer))
            else:
                writer(strings.show_dealer_hand_up(state))

            state.stage = GameStage.UPDATE_BANK

        case GameStage.UPDATE_BANK:

            if len(state.player_completed) == 1 and rules.is_natural(state.player_completed[0]):
                # winning logic specifically for naturals has not yet been applied. The first natural check just said to change stage.
                state.bank += rules.bet_hand(state.player, state.dealer, state.bet, win_odds=PayoutOrd.THREE_TWO)

            else:
                state.bank += rules.winnings(state.player_completed, state.dealer, state.bet)

            writer(strings.show_bank(state))

            state.player_completed = []
            state.stage = GameStage.COMPLETE

        case GameStage.COMPLETE:

            # tear down the state so that we can notice unexpected behavior with None if we start over
            for field in fields(state):
                if field.name not in ['bank', 'deck']:
                    setattr(state, str(field), None)

            state.stage = GameStage.ASK_BET
            #state.bank = None
            # deck is allowed to persist

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
            return io.input_require(int, strings.ask_bank(), strings.ask_bank_fail(), reader, writer)
        init_state = GameState(GameStage.ASK_BET, make_deck_epoch(), ask_bank(), None, None, None, None)

        while not ext_stop_pred.is_set():
            if len(init_state.deck) <= 13: # this is arbitrary for the moment while other details are realized.
                init_state.deck = make_deck_epoch()
                writer(strings.show_shuffling(init_state))
            writer(str(init_state.stage))
            transition_logic(init_state, strings, reader, writer)

    except KeyboardInterrupt:
        writer(strings.show_keyboard_interrupt(init_state))
