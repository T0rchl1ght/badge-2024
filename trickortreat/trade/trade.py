import json
import os
import datetime


DATA_DIR = "data"
TRANSACTION_FILE = "transactions.json"
SETTINGS_FILE = "settings.json"


def init_transactions():
    """
    Make a transaction file
    """
    transactions = {}
    tpath = os.path.join(DATA_DIR, TRANSACTION_FILE)
    with open(tpath, 'w') as f:
        json.dump(transactions, f)


def make_trade(username, candy, number):
    """
    Make a trade given a username, candy and number
    """
    return {"username": username,
            "candy": candy,
            "number": number}


def balance_books(send, receive, candy_settings):
    """
    Given a send trade and a receive trade,
    Add candy to the settings or negate candy from the settings
    """
    # only negate candy if you actually sent some
    if send.get("candy"):
        scandy = send["candy"]
        candy_settings[scandy]["number"] = candy_settings[
            scandy]["number"] - int(send["number"])
    # always receive candy
    rcandy = receive["candy"]
    if rcandy in candy_settings.keys():
        # add to existing candy settings
        candy_settings[rcandy]["number"] = candy_settings[
            rcandy]["number"] + int(receive["number"])
    else:
        # create new candy
        candy_settings[rcandy] = {"number": receive["number"],
                                  "rank": 0}
        # ask for new candy rank
        new_rank = input(f"Give your new candy {rcandy} a rank"
                         f" from 1 to {len(candy_settings.keys())}:\n")
        candy_settings[rcandy]["rank"] = new_rank
    return candy_settings


def record_trade(send, receive):
    """
    Record transaction with what was sent and what was received.
    Then balance the books
    """
    tpath = os.path.join(DATA_DIR, TRANSACTION_FILE)
    spath = os.path.join(DATA_DIR, SETTINGS_FILE)

    with open(tpath) as f:
        transactions = json.load(f)

    with open(spath) as f:
        settings = json.load(f)

    # record the transaction
    transactions[datetime.datetime.now().astimezone().isoformat()] = {
        "send": send,
        "receive": receive}
    with open(tpath, 'w') as f:
        json.dump(transactions, f)
    # balance books
    settings["candy"] = balance_books(send, receive, settings["candy"])
    with open(spath, 'w') as f:
        json.dump(settings, f)
