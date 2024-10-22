# from disp import disp
# import terminalio
# import displayio
# import random
# from ssd1306_ui import box
# from adafruit_display_text.label import Label

# BLACK=0x000000
# WHITE=0xFFFFFF

# this class manages the home display and navigation
# it also presents the new user process when no name is defined
class home:
    def __init__(self, l_disp, dpad):
        # self.group=group
        self.dpad = dpad
        self.game = None
        self.thanks = False  # we have 2 main displays, directions and thanks
        self.disp = l_disp
        self.event_name = "BSidesPDX '24"

        self.disp.setHeader(self.event_name)

        # ToDo: breakout badge setup into it's own thing, should be checked in code.py
        # get the username from file. This duplicates the work done by game.read_name()
        # but i'd rather add file i/o here than add display management there
        try:
            with open("data/myname.txt", "r") as file:
                name = file.readline().rstrip()
        except OSError as e:
            print(e)
            name = ""

        # if there's no file or it's blank, give some instructions and ask for a name
        # ToDo: Move to config?
        # ToDo: Break out the instructions message into a config item
        if name == "":
            self.showAndWait("Welcome to BSides PDX Trick or Treat! Press any button.")
            self.showAndWait(
                ["5-way       (^)", "d-pad    (<)(x)(>)", "buttons:    (v)"]
            )
            self.showAndWait(["Pick a", "name/handle", "to share"])
            self.showAndWait(["(<)(>)(^)(v) to", "highlight a letter", "(x) to select"])
            self.showAndWait(['"," in the bottom', "left to", "change keyboard"])
            self.showAndWait(
                ['"<" Backspace and', '">" Done, both', "in the bottom right"]
            )

            # nameEntry blocks, not fixing
            name = self.nameEntry()

            self.showAndWait(
                ["Welcome " + name + "!", "(^) to trade", "candy and handles"]
            )
            self.showAndWait(
                ["(<) to see friends", "(<)(<) to settings", "(>) to see candy!"]
            )
            self.showAndWait(
                ["Collect 5+ to redeem", "digital candy for", "the real thing!"]
            )

    def showAndWait(self, text):
        self.disp.setText(text, align="c")
        self.dpad.update()
        while not self.dpad.x.fell:
            self.dpad.update()

    # show a string and handle text input
    def nameEntry(self):
        keyboards = [
            ["Q W E R T Y U I O P ", "A S D F G H J K L   ", ", Z X C V B N M < > "],
            ["q w e r t y u i o p ", "a s d f g h j k l   ", ", z x c v b n m < > "],
            ["1 2 3 4 5 6 7 8 9 0 ", "! @ # $ % & * ( )   ", ",   ? [ ] + - . < > "],
        ]
        kbindex = 0
        keyboard = keyboards[0]
        player_name = [" "] * 20  # max name length
        kx = 0
        ky = 0
        nindex = 0
        player_name[nindex] = keyboard[ky][kx]
        self.disp.setHeader("handle:" + "".join(player_name))
        self.disp.setTextCursor(keyboard, (kx, ky))

        while True:
            self.dpad.update()
            if self.dpad.u.fell:
                # u increments through the character set for names
                ky = (ky - 1) % len(keyboard)
            elif self.dpad.d.fell:
                # d decrements through the character set for names
                ky = (ky + 1) % len(keyboard)
            elif self.dpad.l.fell:
                # l moves to the previous char
                kx = (kx - 2) % len(keyboard[ky])
            elif self.dpad.r.fell:
                # r moves to the next char
                kx = (kx + 2) % len(keyboard[ky])
            elif self.dpad.x.fell:
                # "," means cycle keyboards
                if keyboard[ky][kx] == ",":
                    kbindex = (kbindex + 1) % len(keyboards)
                    keyboard = keyboards[kbindex]
                # "<" means backspace
                elif keyboard[ky][kx] == "<" and nindex > 0:
                    player_name[nindex] = " "
                    nindex = nindex - 1
                # ">" means done.
                elif keyboard[ky][kx] == ">":
                    player_name[nindex] = "\n"
                    self.disp.setText("Saving handle")
                    # todo:add confirmation
                    try:
                        with open("data/myname.txt", "w") as file:
                            file.write("".join(player_name))
                    except OSError as e:
                        print(e)
                    print("player_name: {}".format("".join(player_name)))
                    return str.rstrip("".join(player_name))
                # any other letter: append to name
                else:
                    nindex = nindex + 1
            else:
                continue
            # refresh
            player_name[nindex] = keyboard[ky][kx]
            self.disp.setHeader("handle:" + "".join(player_name))
            self.disp.setTextCursor(keyboard, (kx, ky))

    def update(self):
        # show contents, process keypresses
        # self.disp.hidden=False
        header=self.event_name
        body=""

        if self.thanks:
            header="Sponsors"
            body=   ["Thank you to our",
                    "Silver Sponsors:",
                    "BPM",
                    "SecuringHardware.com",
                    ]
            
        self.disp.setHeader(header)
        if self.disp.setText(body):
            if self.dpad.u.fell:
                return "trade"
            elif self.dpad.d.fell:
                return "sleep"
        if self.dpad.x.fell:
            self.thanks = not self.thanks
        elif self.dpad.l.fell:
            return "friends"
        elif self.dpad.r.fell:
            return "candies"
        return "home"
