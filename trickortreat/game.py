#!/usr/bin/env python
from settings import settings
from ui import text
from trade import trade
from trade import trader


def setup():
    """
    Setup routine:
        1. generate a settings file
        2. Ask for a username
        3. Ask for rankings
        4. Save to settings
        5. Generate a transaction file
    """
    print(text.setup_info)
    settings.generate_settings()
    username = input(text.ask_username)
    settings.SETTINGS["username"] = username
    print(text.welcome_msg.format(username=username))
    print(text.show_candies)
    print(", ".join(settings.get_candies()))
    print(text.ask_candy_rank.format(ncandies=len(settings.get_candies())))
    for c in settings.get_candies():
        rank = input(text.loop_entry.format(entry=c))
        settings.SETTINGS["candy"][c]["rank"] = rank
    print(text.show_rank)
    print(settings.show_candies())
    settings.save_settings()
    trade.init_transactions()


def trading():
    """
    Trade routine:
        1. Choose trade or steal
        2. Enter trade: type of candy and number
        3. If trade, enter a send into the ledger. If steal, don't enter a
        send
    Repeat until some keypress
    """
    yestrade = input("Ready to trade? Type 'y' for yes or 'n' for no:\n")
    while yestrade == 'y':
        print(text.tot_info)
        print(text.trade_type)
        choice = input(text.ask_trade_type)
        # generate a trader to exchange things
        print(text.trade_info)
        receive = trader.generate_trade()
        print(trader.show_trade(receive))
        print(text.toggle_info)
        accept = input("Accept trade? Type 'y' for yes or 'n' for no:\n")
        if accept == 'n':
            print(text.reject_trade)
            print("OK no problem!\n")
            continue
        else:
            print(text.accept_trade)
            print(text.show_available_candies)
            print(settings.show_candies())
            print("Enter trade:\n")
            candy = input("Candy:\n")
            number = input("Number:\n")
            print("Trading...")
            if choice == 't':
                print(text.trade_choice)
                send = trade.make_trade(settings.SETTINGS["username"],
                                        candy,
                                        number)
            else:
                print(text.steal_choice)
                send = {"username": "XD",
                        "candy": "",
                        "number": 0}
            trade.record_trade(send, receive)
            settings.load_settings()
            print("Trade Done!\n")
            yestrade = input(
                "Make another trade? Type 'y' for yes or 'n' for no:\n")
    print("Goodbye!\n")


if __name__ == "__main__":
    print(text.intro)
    if not settings.is_in_progress():
        # setup
        setup()
    trading()
