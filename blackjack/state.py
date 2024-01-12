from enum import Enum
from typing import Union, Optional
from dataclasses import dataclass

from blackjack.cards import Deck, Hand
from blackjack.rules import Split

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
    stage : GameStage
    deck : Deck
    bank : int
    bet : Optional[int]
    dealer : Optional[Hand]
    player : Optional[Union[Hand, Split]] # TODO decouple for multiple players
    player_completed : Optional[Split]
