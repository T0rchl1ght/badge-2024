import json
import os

import random
from settings import candy

"""
Settings contain:
    username
    candy number
    candy rank
"""
DATA_DIR = "data"
SETTINGS_FILE = "settings.json"
SETTINGS = {}


def generate_settings():
    """
    At the start of the game, the candy names
    and number are generated at random.
    The type of candies available can be found in
    candy.py
    """
    global SETTINGS
    SETTINGS["candy"] = {}
    # Pick a number between 5 and 7
    # This is the total number of candies assigned
    for count in range(random.randint(5, 7)):
        # Pick a random candy
        icandy = random.randint(0, len(candy.CANDY) - 1)
        # Pick a random number for this candy
        # Make it reasonable
        ncandy = random.randint(1, 10)
        # update the candy settings
        SETTINGS["candy"][candy.CANDY[icandy]] = {"number": ncandy, "rank": 0}


def load_settings():
    """
    Load settings data
    This should be used when a game is restarted
    """
    fpath = os.path.join(DATA_DIR, SETTINGS_FILE)
    if os.path.exists(fpath):
        with open(fpath) as f:
            global SETTINGS
            SETTINGS = json.load(f)


def save_settings():
    """
    Save any changes in settings
    This should be done any time there is an exchange
    of candy
    """
    fpath = os.path.join(DATA_DIR, SETTINGS_FILE)
    with open(fpath, "w") as f:
        global SETTINGS
        json.dump(SETTINGS, f)


def get_candies():
    """
    Return a list of available candies
    """
    # First check if settings has candy
    global SETTINGS
    candy = SETTINGS.get("candy", "")
    if not candy:
        # No candy in RAM? See if it's on file
        load_settings()
    # Try again
    candy = SETTINGS.get("candy", "")
    if candy:
        return candy.keys()
    return []


def show_candies():
    """
    Return a list of candies with their rank in a formatted string
    """
    status = "candy\tnumber\trank\n"
    for c, stat in SETTINGS["candy"].items():
        status = status + f"{c}\t{stat['number']}\t{stat['rank']}\n"
    return status


def is_in_progress():
    """
    If there is a game going, then return true
    else return false.
    A game is in progress if the settings.json
    file exists and has a username.
    If there is a settings file but no username,
    then the game still needs to be set up.
    """
    # check if SETTINGS is already loaded
    global SETTINGS
    if not SETTINGS.get("username", ""):
        # load settings from file and try again
        load_settings()
        if not SETTINGS.get("username", ""):
            # game is not in progress
            return False
        # yes, we have a file and there is a username
        return True
    # yes, we have a file and there is a username
    return True
