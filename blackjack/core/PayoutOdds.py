# this is its own module because multiple modules depend on this one in such a way that there would be circular dependencies
from enum import Enum

class PayoutOdds(Enum):
    # although these are named as they are, the same ord can represent alternatives (ie six_five) according to house rules.
    ONE_ONE = 1,
    THREE_TWO = 2,
    TWO_ONE = 3
