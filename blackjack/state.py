from enum import Enum
from typing import List, TypeVar
from dataclasses import dataclass

from blackjack.cards import Deck, Hand

class FocusList(List[TypeVar('T')]):
    def __init__(self, *args):
        super().__init__(args)
        self._cindex = 0

    def current(self):
        return self[self._cindex]

    def has_next(self) -> bool:
        # remember > does not mean >=
        return len(self) > self._cindex + 1

    def next(self):
        if self.has_next():
            self._cindex += 1
            return self[self._cindex]
        else:
            raise StopIteration

    def reset(self):
        self._cindex = 0

class GameStage(Enum):
    ASK_BET = 0
    INIT_DEAL = 10
    ASK_INSURANCE = 11
    ASK_SPLIT = 20
    PLAYER_ACTIONS = 30 
    PLAYER_DONE = 40
    UPDATE_BANK = 41
    COMPLETE = 50

@dataclass
class GameState:
    # as a general guide for type safety, I've ordered this by roughly when they're initialized in the game. if you inspect at runtime you might be able to spot obvious bugs if there's a None before a non-None.
    stage : GameStage
    deck : Deck
    bank : int
    bet : int
    player : FocusList[Hand]
    dealer : Hand
