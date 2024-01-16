from enum import Enum
from typing import List
from dataclasses import dataclass

from blackjack.core.cards import Deck, Hand

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
    player : List[Hand]
    current_hand : int
    dealer : Hand
