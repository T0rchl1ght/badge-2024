import terminalio
import displayio

BLACK=0x000000
WHITE=0xFFFFFF

#friends manage the friend list. This persists across games. since one friend can give
#you multiple candies, there's a little more work to add that list of candies
class friends:
    def __init__(self, l_disp,  dpad, game):
        #self.group=group
        self.dpad=dpad
        self.game=game

        self.disp = l_disp
        self.details = False

    def update(self):
        #there are 3 lines displayed. The middle line is the 'selected' one
        #and has a > in front
        friendnames=list(self.game.friends.keys())
        #self.group.hidden=False
        scroll = False


        if self.details:
            # ToDo: Convert this into a pretty pop-up
            self.disp.setHeader(friendnames[self.friend_selected])
            scroll = self.disp.setText( 
                [friendnames[self.friend_selected], "said it wasn't:"] + self.game.friends[friendnames[self.friend_selected]]
            )
        else:
            self.disp.setHeader("Friends")  # ToDo: it might be nice to show our own name here
            scroll = self.friend_selected = self.disp.setTextGetSelect(friendnames)
            if self.friend_selected >= 0:
                print("[friends] Selected item {} - {}".format(self.friend_selected, friendnames[self.friend_selected]))
                self.details = True
                # skip processing dpad, so we will display the right thing in the next loop
                return "friends"

        if self.dpad.l.fell:
            #self.group.hidden=True
            self.details = False
            return "settings"
        elif self.dpad.r.fell:
            #self.group.hidden=True
            self.details = False
            return "home"
        elif self.dpad.x.fell:
            self.details = not self.details
        return "friends"
