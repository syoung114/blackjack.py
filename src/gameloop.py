from typing import Callable

def gameloop(deck : Deck, print_fn : Callable[[str], None], writer : Callable[..., str]):
    while len(deck) > 0:
        player_hand = init_hand(deck)
        dealer_hand = init_hand(deck)

