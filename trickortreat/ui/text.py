"""
Text Messages for the UI
"""

intro = """
Welcome to the Trick or Treat game!

This is a command line demo of the game.
As such, there is no navigation like up, down, left, right, or enter.
Instead, I will indicate how I simulate it.

Every time a game routine starts, I will give a blurb on what is supposed
to happen. Hopefully, this should be enough to transcribe the actions to the
dpad.
"""

setup_info = """
We are in setup mode!

There is either no settings.json file in the data folder or there is no
username in the settings.json file. If this is the case, you ask for the
username and then ask them to rank candies from 1 to the number of candies
they have. I still don't know if you can give multiple candies the same
ranking or not, so I'm not coding for that yet.

I am not sure how dpad inputs for alphanumeric characters work but the
only one I have simulated here is enter.
"""

ask_username = "\nEnter your username: \n"
welcome_msg = "\nWelcome {username}!\n"
show_candies = "\nYou have the following candies: \n"
ask_candy_rank = "\nRank your candies from 1 to {ncandies}: \n"
loop_entry = "{entry}: "
show_rank = "\nYou have ranked your candies like this: \n"

trade_info = """
We are in trade mode!

Since there is a settings.json file in the data folder and there is a
username, we will jump right into trading.

If you want to go into setup mode, just delete the settings.json file in the
data folder. I still don't know whether I want the game to allow users to
start again.
"""

tot_info = """
First, you have to choose to trade or steal.
I imagine there is a yes/no or trade/steal selection to make before pressing
enter. Here I am simulating it by entering either "t" or "s"
"""

ask_trade_type = "Make your choice:\n"
trade_type = """
Do you want to trade candy or steal candy?
Type t to trade or s to steal and press enter.
"""

show_available_candies = "\nYou have the following candies to trade: \n"

trade_info = """
To simulate another person trading, a trader will be automatically
generated. You will be asked to accept or reject and another trader
will be generated until you accept a trade.
This doesn't have to be implemented. It's just to simulate another
person."""
ask_trade = "\nEnter your trade:\n"

toggle_info = """
yes/no toggle is simulated by typing 'y' or 'n'
"""

reject_trade = """
Rejecting a trade starts the trade sequence again
Remember: this is to simulate negotiation. Do not include the trader code!
"""

accept_trade = """
Now pick the candy and the number. I think providing a list of choices from
the available candies is good here.
"""

trade_choice = """
If the original choice was to trade, the trading goes on as normal
"""

steal_choice = """
If the original choise was to steal, a fake trade overwrites the original
trade and shows up in the transactions. To see the transactions, open the
transactions.json file in the data folder.
"""
