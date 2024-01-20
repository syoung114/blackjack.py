from functools import partial
from typing import Callable

from blackjack.core import constants
from blackjack.core.io import io
from blackjack.core.io.InputProvider import InputProvider
from blackjack.core.state import GameState, PlayerAction

from blackjack.core.exception.StupidProgrammerException import StupidProgrammerException

class BareInput(InputProvider):
    # I've made sure the strings don't cross innopropriate contexts. You can use find/replace to quickly change them without problems. I've realized having static getter methods to hold the strings not worth the maintenance effort.

    @staticmethod
    def input_bank(reader : Callable[..., str], writer : Callable[[str], None]) -> int:
        constraint = io.Constraint(int).at_least(constants.MIN_BET)
        return io.input_require(constraint, "prompt_bank", "prompt_bank_fail", reader, writer)

    @staticmethod
    def input_bet(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> int:
        bet_constraint = io.Constraint(int).within(constants.MIN_BET, state.bank)
        bet = io.input_require(bet_constraint, "prompt_bet", "prompt_bet_fail", reader, writer) 
        return bet

    @staticmethod
    def input_hit(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> PlayerAction:
        return PlayerAction.HIT if \
            io.ask_binary(
                "hit",
                "stay",
                "prompt_hit_stay",
                "prompt_hit_stay_fail",
                reader,
                writer,
            ) \
        else PlayerAction.STAY

    @staticmethod
    def input_want_split(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> bool:
        return io.ask_binary("yes", "no", "prompt_split", "prompt_split_fail", reader, writer)

    @staticmethod
    def input_want_insurance(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> bool:
        return io.ask_binary("yes", "no", "prompt_insurance", "prompt_insurance_fail", reader, writer)

    @staticmethod
    def input_hit_stay_double(state : GameState, reader : Callable[..., str], writer : Callable[[str], None]) -> PlayerAction:
        constraint = io.Constraint(str).equalsAny("hit", "stay", "double")
        user = io.input_require(constraint, "prompt_hit_stay_double", "prompt_hit_stay_double_fail", reader, writer)

        # I realized matches/switches are just partial equality functions.
        # you can't call a function in a case statement so this is a clever workaround (if I say so myself) which still maintains the expressiveness of match/switch
        user_match = partial(lambda a,b: a==b, user)
        if user_match("double"):
            return PlayerAction.DOUBLE

        if user_match("hit"):
            return PlayerAction.HIT

        if user_match("stay"):
            return PlayerAction.STAY

        raise StupidProgrammerException("missing case in input_hit_stay_double")
