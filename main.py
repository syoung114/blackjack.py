from threading import Event

from blackjack.core import driver
from blackjack.core.io.BareInput import BareInput
from blackjack.core.io.BareOutput import BareOutput


def main():
    driver.driver_io(Event(), BareInput, BareOutput)

if __name__ == "__main__":
    #import argparse
    #parser = ArgumentParser("blackjack.py: Play and analyze Blackjack though human methods and machine learning")
    main()
