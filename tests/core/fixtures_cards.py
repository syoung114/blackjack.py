import pytest

from blackjack.core.cards import Card, Rank, Suit

@pytest.fixture
def fix_rseed_zero_deck():
    # generated by getting the output with seed 0 in the python repl and cleaning with the Haskell script.
    # randomness is fundamentally difficult to reason about so I think just ensuring that ordering doesn't change given equal seeds is the best approach.
    return [Card(Rank.THREE,Suit.HEART),Card(Rank.KING,Suit.CLUB),Card(Rank.SEVEN,Suit.SPADE),Card(Rank.THREE,Suit.SPADE),Card(Rank.KING,Suit.HEART),Card(Rank.EIGHT,Suit.CLUB),Card(Rank.SIX,Suit.CLUB),Card(Rank.JACK,Suit.HEART),Card(Rank.TWO,Suit.CLUB),Card(Rank.JACK,Suit.SPADE),Card(Rank.EIGHT,Suit.HEART),Card(Rank.ACE,Suit.CLUB),Card(Rank.FIVE,Suit.CLUB),Card(Rank.TEN,Suit.HEART),Card(Rank.EIGHT,Suit.DIAMOND),Card(Rank.TWO,Suit.DIAMOND),Card(Rank.KING,Suit.SPADE),Card(Rank.FOUR,Suit.HEART),Card(Rank.NINE,Suit.HEART),Card(Rank.SIX,Suit.SPADE),Card(Rank.ACE,Suit.SPADE),Card(Rank.QUEEN,Suit.CLUB),Card(Rank.FOUR,Suit.SPADE),Card(Rank.FIVE,Suit.DIAMOND),Card(Rank.THREE,Suit.DIAMOND),Card(Rank.JACK,Suit.CLUB),Card(Rank.NINE,Suit.DIAMOND),Card(Rank.TWO,Suit.HEART),Card(Rank.QUEEN,Suit.SPADE),Card(Rank.JACK,Suit.DIAMOND),Card(Rank.FOUR,Suit.CLUB),Card(Rank.FIVE,Suit.SPADE),Card(Rank.TEN,Suit.CLUB),Card(Rank.NINE,Suit.SPADE),Card(Rank.SEVEN,Suit.CLUB),Card(Rank.TWO,Suit.SPADE),Card(Rank.SIX,Suit.DIAMOND),Card(Rank.NINE,Suit.CLUB),Card(Rank.EIGHT,Suit.SPADE),Card(Rank.ACE,Suit.DIAMOND),Card(Rank.QUEEN,Suit.HEART),Card(Rank.TEN,Suit.DIAMOND),Card(Rank.FIVE,Suit.HEART),Card(Rank.SEVEN,Suit.DIAMOND),Card(Rank.KING,Suit.DIAMOND),Card(Rank.SIX,Suit.HEART),Card(Rank.SEVEN,Suit.HEART),Card(Rank.FOUR,Suit.DIAMOND),Card(Rank.THREE,Suit.CLUB),Card(Rank.ACE,Suit.HEART),Card(Rank.TEN,Suit.SPADE),Card(Rank.QUEEN,Suit.DIAMOND)]

@pytest.fixture
def fix_deck_alphabetical_52():
    suits = [Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE]
    ranks = [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
    
    deck = [(rank, suit) for suit in suits for rank in ranks]
    
    return deck

@pytest.fixture
def fix_deck_clubs_12():
    ranks = [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
    return [(rank, Suit.CLUB) for rank in ranks]

@pytest.fixture
def fix_deck_diamonds_12():
    ranks = [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
    return [(rank, Suit.DIAMOND) for rank in ranks]
