from blackjack.cards import Card, Rank, Suit

# TODO might be interesting to change these values (as long as they have same length and value) and see if any tests fail. In fact, you could write a script that generates these helper functions.

def hand_2C():
    # for whenever you need just one card.
    return [Card(Rank.TWO,Suit.CLUB)]

def hand_2D():
    return [Card(Rank.TWO,Suit.DIAMOND)]

def hand_2H():
    return [Card(Rank.TWO,Suit.HEART)]

def hand_2C2D():
    # what's special about this one is it's a hand with lowest initial value, 4. One ace is 11 in initial hand
    return [Card(Rank.TWO,Suit.CLUB),Card(Rank.TWO,Suit.DIAMOND)]

def hand_blackjack_ace_up():
    return [Card(Rank.ACE, Suit.CLUB), Card(Rank.JACK, Suit.CLUB)]

def hand_blackjack_ace_down():
    return [Card(Rank.JACK, Suit.CLUB), Card(Rank.ACE, Suit.CLUB)]

def hand_empty():
    return []

def hand_bust_1():
    # value==22
    return [Card(Rank.NINE, Suit.CLUB), Card(Rank.SIX, Suit.DIAMOND), Card(Rank.TWO, Suit.HEART), Card(Rank.FIVE, Suit.SPADE)]

def hand_bust_2():
    # value==23, because you don't want false answer with 22==23
    return [Card(Rank.KING, Suit.CLUB), Card(Rank.QUEEN, Suit.DIAMOND), Card(Rank.THREE, Suit.HEART)]

def hand_bust_dealer():
    # value==22
    return [Card(Rank.TEN, Suit.CLUB), Card(Rank.SIX, Suit.DIAMOND), Card(Rank.SIX, Suit.HEART)]

def hand_18_len_2():
    return [Card(Rank.QUEEN, Suit.CLUB), Card(Rank.EIGHT, Suit.DIAMOND)]

def hand_17_len_2():
    return [Card(Rank.ACE, Suit.CLUB), Card(Rank.SIX, Suit.DIAMOND)]

def hand_17_len_3():
    return [Card(Rank.SEVEN, Suit.CLUB), Card(Rank.THREE, Suit.DIAMOND), Card(Rank.SEVEN, Suit.HEART)]

def hand_18_len_3():
    return [Card(Rank.ACE, Suit.CLUB), Card(Rank.THREE, Suit.DIAMOND), Card(Rank.FOUR, Suit.HEART)]

