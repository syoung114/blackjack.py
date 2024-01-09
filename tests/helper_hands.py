from blackjack.cards import Card, Rank, Suit

def hand_2C():
    return [Card(Rank.TWO,Suit.CLUB)]

def hand_2D():
    return [Card(Rank.TWO,Suit.DIAMOND)]

def hand_2H():
    return [Card(Rank.TWO,Suit.HEART)]

def hand_2C2D():
    return [Card(Rank.TWO,Suit.CLUB),Card(Rank.TWO,Suit.DIAMOND)]

def hand_blackjack_ace_up():
    return [Card(Rank.ACE, Suit.CLUB), Card(Rank.JACK, Suit.CLUB)]

def hand_blackjack_ace_down():
    return [Card(Rank.JACK, Suit.CLUB), Card(Rank.ACE, Suit.CLUB)]

def hand_empty():
    return []

