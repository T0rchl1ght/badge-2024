import random

from settings import candy

"""
Trader simulates another trader to trade candy with.
The trader randomly generates their own username and
candy to trade with you.
"""

USERNAMES = [
    "Acid Burn",
    "Phantom Phrek",
    "Lord Nikon",
    "The Plague",
    "Zero Cool",
    "Crash Override",
    "Cereal Killer",
    "apoc",
    "cypher",
    "dozer",
    "ghost",
    "morpheus",
    "mouse",
    "neo",
    "switch",
    "tank",
    "trinity",
    "oracle",
    "ed",
    "w1n5t0n",
    "m1k3y"]


def generate_trade():
    """
    When you "trade" the trader will say they have
    certain candy to trade with you.
    """
    global USERNAMES
    # pick a username
    iuser = random.randint(0, len(USERNAMES) - 1)
    # pick a candy
    icandy = random.randint(0, len(candy.CANDY) - 1)
    # pick a candy number
    # make it reasonable
    ncandy = random.randint(1, 3)
    # return a trade
    return {"username": USERNAMES[iuser],
            "candy": candy.CANDY[icandy],
            "number": ncandy}


def show_trade(trade):
    """
    Given a trade dictionary of the form:
        {username: username,
        candy: type of candy,
        number: number of candies}
    Print it out
    """
    return (f"{trade['username']} would like to trade {trade['number']}"
            f" {trade['candy']}\n")
