import threading
import time
import random

from enum import Enum
from typing import Callable, Union
from dataclasses import dataclass, fields

from blackjack import rules, cards, io

from blackjack.cards import Hand, Deck
from blackjack.rules import PayoutOrd, Split
from blackjack.exception.StupidProgrammerException import StupidProgrammerException
from blackjack.strings.StringProvider import StringProvider

class GameStage(Enum):
    ASK_BET = 0
    INIT_DEAL = 10
    ASK_SPLIT = 20
    PLAYER_ACTIONS = 30 
    PLAYER_DONE = 40
    UPDATE_BANK = 41
    COMPLETE = 50

@dataclass
class GameState:
    stage : GameStage
    deck : Deck
    bank : int
    bet : int
    dealer : Hand
    player : Union[Hand, Split]# TODO decouple for multiple players
    player_completed : Split

def make_deck_epoch():
    def _epoch_time_ms():
        return round(time.time() * 1000)

    epoch = _epoch_time_ms()
    seed = random.Random(epoch)
    return cards.make_deck_unordered(seed) 

def transition_logic(data : GameState, strings : StringProvider, reader : Callable[..., str], writer : Callable[[str], None]):
    """
    Given a GameStage and related data, returns the updated data according to blackjack logic and user input. Implemented as a state machine/pattern matching.

    Impure, but is wrappable for pure interface

    @arg data A GameState representing a snapshot of the working state
    """
    def input_require(dtype, prompt, prompt_fail):
        # The reader and writer do not change so typing it repeatedly is annoying
        return io.input_require(dtype, prompt, prompt_fail, reader, writer)

    def ask_bank() -> int:
        return input_require(int, strings.ask_bank(), strings.ask_bank_fail())
 
    def ask_bet(bank) -> int:
        bet_constraint = io.Constraint().require(int).within(0,bank)
        bet = input_require(bet_constraint, strings.ask_bet(), strings.ask_bet_fail())
        return bet

    def ask_hit() -> bool:
        """
        @returns true if hit, false if stay.
        """
        hs_constraint = io.Constraint().equalsAny(strings.input_hit(), strings.input_stay())
        do_hs = input_require(hs_constraint, strings.ask_hit_stay(), strings.ask_hit_stay_fail())
        return do_hs == strings.input_hit()

    def ask_want_split() -> bool:
        split_constraint = io.Constraint().require(str).equalsAny(strings.input_yes(), strings.input_no())
        do_split = input_require(split_constraint, strings.ask_split(), strings.ask_split_fail())
        return do_split == strings.input_yes()

    def ask_want_insurance() -> bool:
        insurance_constraint = io.Constraint().require(str).equalsAny(strings.input_yes(), strings.input_no())
        do_insurance = input_require(
            insurance_constraint,
            strings.ask_insurance(),
            strings.ask_insurance_fail()
        )
        return do_insurance == strings.input_yes()

    def handle_init_hand(deck : Deck):
        player = rules.init_hand(deck)
        dealer = rules.init_hand(deck)
        writer(
            strings.initial_hand(player, dealer)
        )
        return player, dealer

    def handle_insurance(dealer : Hand, bet : int):
        ins_status = False
        side_bet = rules.insurance_make_side_bet(bet)
        ins_status, side_bet_winnings = rules.insure(dealer, side_bet)
        if ins_status:
            writer(strings.show_insurance_success())
        else:
            writer(strings.show_insurance_fail())
        return ins_status, side_bet_winnings

    match data.stage:
        case GameStage.ASK_BET:
            new_bank = ask_bank()

            #data.deck = make_deck_epoch()
            data.bank = new_bank
            data.bet = ask_bet(new_bank)
            data.stage = GameStage.INIT_DEAL

        case GameStage.INIT_DEAL:
            # deal the player and dealer. modifies the deck via side effect in the process.
            new_player, new_dealer = handle_init_hand(data.deck)

            if rules.is_natural(new_player):
                winnings = rules.compare(new_player, new_dealer, data.bet, payout_ord=PayoutOrd.THREE_TWO)

                data.bank += winnings
                data.stage = GameStage.ASK_BET

            # check and handle insurance
            elif rules.is_insurable(new_dealer) and ask_want_insurance():
                ins_success, side_bet_payout = handle_insurance(new_dealer, data.bet)

                data.player = new_player
                data.dealer = new_dealer
                data.bank += side_bet_payout
                data.stage = GameStage.ASK_BET if ins_success else GameStage.ASK_SPLIT

            # either not insurable or they don't want insurance, so move on
            else:
                data.player = new_player
                data.dealer = new_dealer
                data.stage = GameStage.ASK_SPLIT

        case GameStage.ASK_SPLIT:
            if rules.can_split(data.player) and ask_want_split():

                data.player = rules.init_split(data.player, data.deck)
                data.stage = GameStage.PLAYER_ACTIONS

            else:
                data.stage=GameStage.PLAYER_ACTIONS

        case GameStage.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular isn't as true to the state machine model

            #is_split = all(isinstance(elem,list) for elem in data.player) # a more naive but faster way is to check if first element is a list (cards are tuples)
            is_split = isinstance(data.player[0],list)
            current_hand = data.player[len(data.player) - 1] if is_split else data.player

            hand_completed = False

            if ask_hit():
                cards.take_card(current_hand, data.deck)

                if rules.is_bust(current_hand):
                    writer(strings.show_bust(current_hand))
                    hand_completed = True
                else:
                    writer(strings.show_hand_status(current_hand))

            else:
                hand_completed = True

            if hand_completed:
                # Because splits and hands aren't equal representations we must handle inserting them differently into the player_completed list.

                # Up to this point player_completed has potentially not been used.
                if data.player_completed == None:
                    data.player_completed = []

                if is_split:
                    data.player_completed.append(data.player.pop())

                else:
                    # data.player.pop() doesn't work because that removes a single card
                    data.player_completed.append(data.player)
                    data.player = []

                if len(data.player) == 0:
                    data.stage = GameStage.PLAYER_DONE


        case GameStage.PLAYER_DONE:
            rules.dealer_play(data.dealer, data.deck)

            writer(strings.show_hand_status(data.dealer))
            data.stage = GameStage.COMPLETE

        case GameStage.UPDATE_BANK:

            data.bank += sum([rules.compare(hand, data.dealer, data.bet) for hand in data.player_completed])
            writer(strings.show_bank(data.bank))

            data.player_completed = []
            data.stage = GameStage.COMPLETE

        case GameStage.COMPLETE:

            for field in fields(data):
                if field.name not in ['bank', 'deck']:
                    setattr(data, field, None)

            data.stage = GameStage.ASK_BET
            #data.bank = None
            # deck is allowed to persist

        case _:
            raise StupidProgrammerException(f"missed case {data.stage} in driver.transition_logic")

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
        init_state = GameState(GameStage.ASK_BET, make_deck_epoch(), None, None, None, None, None)
        while not ext_stop_pred.is_set():
            #if len(current_state.deck) < 26:
            #    current_state._replace(deck=make_deck_epoch())
            writer(str(init_state.stage))
            transition_logic(init_state, strings, reader, writer)

    except KeyboardInterrupt:
        writer(strings.show_keyboard_interrupt())
