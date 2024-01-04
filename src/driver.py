import functools
import threading
import time
import random

from enum import Enum
from typing import Callable, List, NamedTuple

from src import blackjack, constants
from src import cards
from src import io

from src.cards import Hand, Deck
from src.blackjack import PayoutOrd, Split
from src.exception.StupidProgrammerException import StupidProgrammerException

from src.strings.StringProvider import StringProvider

class GameState(Enum):
    ASK_BET = 0,
    INIT_DEAL = 10,
    ASK_SPLIT = 20,
    PLAYER_ACTIONS = 30, 
    PLAYER_DONE = 40,
    COMPLETE = 50

class GameData(NamedTuple):
    state : GameState
    deck : Deck
    dealer : Hand
    player : Split # TODO decouple for multiple players
    player_completed : Split
    bank : int
    bet : int

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

    def input_require(a, prompt, prompt_fail):
        # The reader and writer do not change so typing it repeatedly is annoying
        return io.input_require(a, prompt, prompt_fail, reader, writer)

    def ask_bank():
        return input_require(int, strings.ask_bank(), strings.ask_bank_fail())

    def ask_bet(bank):
        bet_constraint = io.Constraint().require(int).within(0,bank)
        bet = input_require(
            bet_constraint,
            strings.ask_bet(),
            strings.ask_bet_fail(),
        )
        return bet

    def handle_init_hand(deck : Deck):
        new_deck = deck.copy() # needed for referential transparency. you could forego this in a more imperative algorithm
        player = blackjack.init_hand(new_deck)
        dealer = blackjack.init_hand(new_deck)
        writer(
            strings.initial_hand(player, dealer)
        )
        return player, dealer, new_deck

    def handle_insurance(dealer : Hand, bet : int):
        ins_status = False
        if blackjack.is_insurable(dealer):
            # ask whether they want to do it
            insurance_constraint = io.Constraint().require(str).equalsOr(strings.input_yes(), strings.input_no())
            do_insurance = input_require(
                insurance_constraint,
                strings.ask_insurance(),
                strings.ask_insurance_fail()
            )
            if do_insurance == strings.input_yes():
                side_bet = blackjack.insurance_make_side_bet(bet)
                ins_status, side_bet_winnings = blackjack.insure(dealer, side_bet)
                if ins_status:
                    writer(strings.show_insurance_success())
                else:
                    writer(strings.show_insurance_fail())
                return ins_status, side_bet_winnings
        return ins_status, 0

    def ask_want_split():
        split_constraint = io.Constraint().require(str).equalsOr(strings.input_yes(), strings.input_no())
        do_split = input_require(split_constraint, strings.ask_split(), strings.ask_split_fail())
        return do_split == strings.input_yes()

    def ask_hit() -> bool:
        """
        @returns true if hit, false if stay.
        """
        hs_constraint = io.Constraint().equalsOr(strings.input_hit(), strings.input_stay())
        do_hs = input_require(hs_constraint, strings.ask_hit_stay(), strings.ask_hit_stay_fail())
        return do_hs == strings.input_stay()

    def logic_atomic(data : GameData) -> GameData:
        """
        Given a GameState and related data, returns the updated data according to blackjack.ckjack logic and user input. Implemented as a state machine/pattern matching.

        @arg data A GameData representing a snapshot of the working state
        """
        match data.state:
            case GameState.ASK_BET:
                return \
                    data._replace(
                        bank = ask_bank(),
                        bet = ask_bet(data.bank),
                        state = GameState.INIT_DEAL
                    )

            case GameState.INIT_DEAL:
                play,deal,dek = handle_init_hand(data.deck)

                if blackjack.is_natural(play):
                    return \
                        data._replace(
                            #player=null_data.player,
                            #dealer=null_data.dealer,
                            deck=dek,
                            bank=data.bank + blackjack.compare(
                                play, deal, data.bet, payout_ord=PayoutOrd.THREE_TWO
                            ), # The LT branch is impossible in this function but it's a convenient call
                            state=GameState.ASK_BET
                        )
                else: # check and handle insurance
                    ins_success, side_bet_payout = handle_insurance(data.dealer, data.bet)
                    return \
                        data._replace(
                            player=[play],
                            dealer=deal,
                            bank=data.bank + side_bet_payout,
                            state=GameState.ASK_BET if ins_success else GameState.ASK_SPLIT
                        )
    
            case GameState.ASK_SPLIT:
                if blackjack.can_split(data.player[0]) and ask_want_split():
                    return data._replace(
                        player=blackjack.init_split(data.player[0]),
                        state=GameState.PLAYER_ACTIONS
                    )
                else:
                    # just continue to next stage
                    return data._replace(
                        state=GameState.PLAYER_ACTIONS
                    )

            case GameState.PLAYER_ACTIONS: # this is more granular than "for split in splits", being every hit/stay prompt. I think being less granular would lead to bugs.

                def split_completion():
                    if len(data.player) > 1:
                        return data._replace(
                            player=data.player[1:],
                            player_completed=data.player_completed+data.player,
                            # do not change state yet
                        )
                    return data._replace(
                        player_completed=data.player_completed+data.player,
                        state=GameState.PLAYER_DONE
                    )
                    

                if ask_hit():
                    new_deck = data.deck.copy()

                    # add new card to current hand
                    new_hand = data.player[0].copy()
                    cards.take_card(new_hand, new_deck)

                    bust = blackjack.is_bust(new_hand)
                    if bust:
                        writer(strings.show_bust(new_hand))
                        return split_completion()
                    else:
                        # concat the current hand with the new card
                        return data._replace(
                            player=new_hand+data.player[1:]
                            # don't change state yet
                        )

                # stay
                return split_completion()

            case GameState.PLAYER_DONE:
                new_dealer = data.dealer.copy()
                new_deck = data.deck.copy()
                d2 = blackjack.dealer_play(new_dealer, new_deck)

                return data._replace(
                    bank=data.bank + sum([blackjack.compare(split, d2, data.bet) for split in data.player_completed]),
                    state=GameState.COMPLETE
                )

            case GameState.COMPLETE:
                return data._replace(
                    player_completed=[],
                    state=GameState.ASK_BET
                )

            case _:
                raise StupidProgrammerException(f"missed case {data.state} in driver.logic_atomic")


    try:
        init_state = GameData(GameState.ASK_BET, make_deck_epoch(), [], [[]], [[]], -1, -1)
        current_state = init_state
        while not ext_stop_pred.is_set():
            if len(current_state.deck) < 26:
                current_state._replace(deck=make_deck_epoch())
            current_state = logic_atomic(current_state)

    except KeyboardInterrupt:
        writer(strings.show_keyboard_interrupt())

