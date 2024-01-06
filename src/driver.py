import threading
import time
import random
import copy

from enum import Enum
from typing import Callable, Optional, Union
from dataclasses import dataclass

from src import blackjack, cards, io

from src.cards import Hand, Deck
from src.blackjack import PayoutOrd, Split
from src.exception.StupidProgrammerException import StupidProgrammerException

from src.strings.StringProvider import StringProvider

class GameStage(Enum):
    ASK_BET = 0
    INIT_DEAL = 10
    ASK_SPLIT = 20
    PLAYER_ACTIONS = 30 
    PLAYER_DONE = 40
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

def driver_io(
    ext_stop_pred : threading.Event,
    strings : StringProvider,
    reader : Callable[..., str] = input,
    writer : Callable[[str], None] = print
):
    """
    Sort of like main() or a blackjack.loop. It's the highest level driver of program logic and it creates the I/O side effects concerning user input and display.
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
        player = blackjack.init_hand(deck)
        dealer = blackjack.init_hand(deck)
        writer(
            strings.initial_hand(player, dealer)
        )
        return player, dealer

    def handle_insurance(dealer : Hand, bet : int):
        ins_status = False
        side_bet = blackjack.insurance_make_side_bet(bet)
        ins_status, side_bet_winnings = blackjack.insure(dealer, side_bet)
        if ins_status:
            writer(strings.show_insurance_success())
        else:
            writer(strings.show_insurance_fail())
        return ins_status, side_bet_winnings

    def transition_logic(data : GameState):
        """
        Given a GameStage and related data, returns the updated data according to blackjack.ckjack logic and user input. Implemented as a state machine/pattern matching.

        Impure, but is wrappable for pure interface

        @arg data A GameState representing a snapshot of the working state
        """
        match data.stage:
            case GameStage.ASK_BET:
                new_bank = ask_bank()

                data.deck = make_deck_epoch()
                data.bank = new_bank
                data.bet = ask_bet(new_bank)
                data.stage = GameStage.INIT_DEAL

            case GameStage.INIT_DEAL:
                # deal the player and dealer. modifies the deck via side effect in the process.
                new_player, new_dealer = handle_init_hand(data.deck)

                if blackjack.is_natural(new_player):
                    winnings = blackjack.compare(new_player, new_dealer, data.bet, payout_ord=PayoutOrd.THREE_TWO)

                    data.bank += winnings
                    data.stage = GameStage.ASK_BET

                # check and handle insurance
                elif blackjack.is_insurable(new_dealer) and ask_want_insurance():
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
                if blackjack.can_split(data.player) and ask_want_split():

                    data.player = blackjack.init_split(data.player, new_deck)
                    data.stage = GameStage.PLAYER_ACTIONS

                else:
                    data.stage=GameStage.PLAYER_ACTIONS

            case GameStage.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular isn't as true to the state machine model

                #is_split = all(isinstance(elem,list) for elem in data.player) # a more naive but faster way is to check if first element is tuple
                is_split = isinstance(data.player[0],list)

                def split_completion():
                    """
                    If split hand, moves the last hand into the completed hand list. If not split, wraps the hand into Split representation and moves it into the completed hand list. Finally, progresses the state if it was the last hand.

                    @arg force_complete Do we state transition even if it's not the last hand?
                    """
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

                current_hand : Hand = data.player[len(data.player)-1] if is_split else data.player
                if ask_hit():
                    cards.take_card(current_hand, data.deck)

                    if blackjack.is_bust(current_hand):
                        writer(strings.show_bust(current_hand))
                        split_completion()
                    else:
                        writer(strings.show_hand_status(current_hand))

                else:
                    split_completion()

            case GameStage.PLAYER_DONE:
                blackjack.dealer_play(data.dealer, data.deck)

                writer(strings.show_hand_status(data.dealer))
                data.stage = GameStage.COMPLETE

            case GameStage.COMPLETE:
                new_bank = sum([blackjack.compare(hand, data.dealer, data.bet) for hand in data.player_completed])
                writer(strings.show_bank(new_bank))

                data.bank=data.bank + new_bank
                data.player_completed = []
                data.stage = GameStage.ASK_BET

            case _:
                raise StupidProgrammerException(f"missed case {data.stage} in driver.transition_logic")


    try:
        init_state = GameState(GameStage.ASK_BET, None, None, None, None, None, None)
        #init_state = GameState(GameStage.ASK_BET, [], -1, -1, [], [], [[]])
        #current_state = copy.deepcopy(init_state)
        while not ext_stop_pred.is_set():
            #if len(current_state.deck) < 26:
            #    current_state._replace(deck=make_deck_epoch())
            writer(str(init_state.stage))
            transition_logic(init_state)

    except KeyboardInterrupt:
        writer(strings.show_keyboard_interrupt())

from threading import Event
from src.strings.StubStrings import StubStrings
driver_io(Event(), StubStrings())
