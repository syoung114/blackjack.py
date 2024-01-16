def main():
    from threading import Event
    from blackjack.core.strings.StubStrings import StubStrings
    from blackjack.core import driver
    driver.driver_io(Event(), StubStrings())

if __name__ == "__main__":
    #import argparse
    #parser = ArgumentParser("blackjack.py: Play and analyze Blackjack though human methods and machine learning")
    main()
