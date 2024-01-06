def main():
    from threading import Event
    from blackjack.strings.StubStrings import StubStrings
    import blackjack.driver as driver
    driver.driver_io(Event(), StubStrings())

if __name__ == "__main__":
    #import argparse
    #parser = ArgumentParser("blackjack.py: Play and analyze Blackjack though human methods and machine learning")
    main()
