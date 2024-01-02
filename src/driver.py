import threading
import time
import random

from typing import Callable

from src.blackjack import PayoutOrd, is_insurable

from . import blackjack as game
from . import cards
from . import io
from . import constants

from cards import Hand, Deck
from StringProvider import StringProvider

def shuffle_deck():
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
    Sort of like main() or a game loop. It's the highest level driver of program logic and it creates the I/O side effects concerning user input and display.
    """

    def input_require(a, prompt, prompt_fail):
        return io.input_require(a, prompt, prompt_fail, reader, writer) # The reader and writer do not change so typing it repeatedly is annoying

    def ask_bank():
        return input_require(int, strings.init_bank(), strings.generic_input_fail())

    def ask_bet(bank):
        bet_constraint = io.Constraint().require(int).within(0,bank)
        bet = input_require(
            bet_constraint,
            strings.ask_bet(),
            strings.generic_input_fail(),
        )
        return bet

    def handle_init_hand(deck):
        player = game.init_hand(deck)
        dealer = game.init_hand(deck)
        writer(
            strings.initial_hand(player, dealer)
        )
        return player, dealer

    def handle_insurance(dealer : Hand, bet : int):
        ins_status = False
        if game.is_insurable(dealer):
            # ask whether they want to do it
            insurance_constraint = io.Constraint().require(str).equalsOr(strings.yes(), strings.no())
            do_insurance = input_require(insurance_constraint, strings.ask_insurance(), strings.ask_insurance_fail())
            if do_insurance == strings.yes():
                side_bet = game.ins_make_side_bet(bet)
                ins_status, side_bet_winnings = game.insure(dealer, side_bet)
                if ins_status:
                    writer(strings.insurance_success())
                else:
                    writer(strings.insurance_fail())
                return ins_status, side_bet_winnings
        return ins_status, 0

    def handle_split(player : Hand) -> List[Hand]:
        if game.can_split(player):
            split_constraint = io.Constraint().require(str).equalsOr(strings.yes(), strings.no())
            do_split = input_require(split_constraint, strings.ask_split(), strings.ask_split_fail())
            if do_split == strings.yes():
                return game.init_split(player)
        return [player]

    def handle_hit_stay(player : Hand, dealer : Hand, deck : Deck, bet : int):
        hs_constraint = io.Constraint().equalsOr(strings.hit(), strings.stay())
        while True:
            do_hs = input_require(hs_constraint, strings.ask_hit_stay(), strings.ask_hit_stay_fail())
            if do_hs == strings.stay() and game.is_bust(player):
                break
            # if the player chose to hit...
            cards.take_card(player, deck)
            writer(strings.hand_status(player))
        _, dealer = game.dealer_play(dealer, deck)
        return game.compare(player,dealer,bet)

    def _driver_io():
        bank = ask_bank()
        while True:
            deck = shuffle_deck()
            while len(deck) > 0:
                # if the external thread indicated a predicate was met
                if ext_stop_pred.is_set():
                    return # this line is the reason I wrap this logic in an inner function. goto would be cleaner for exiting nested whiles but it's not supported in Python
            
                bet = ask_bet(bank)

                # deal the hands and display it. We assume the displayer will hide the second dealer card.
                player, dealer = handle_init_hand(deck)

                # handle naturals for the player and the dealer
                if game.is_natural(player):
                    bank += game.compare(player, dealer, bet, gt_payout_ord=PayoutOrd.THREE_TWO) # The LT branch is impossible in this function but it's a convenient call
                    continue

                ins_success, side_bet_payout = handle_insurance(dealer, bet)
                bank += side_bet_payout
                if ins_success:
                    continue

                splits = handle_split(player)

                for split in splits:
                    bank += handle_hit_stay(split, bet)

    try:
        _driver_io()
    except KeyboardInterrupt:
        writer(strings.keyboard_interrupt())

