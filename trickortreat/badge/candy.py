import displayio
import terminalio
import adafruit_imageload
from ssd1306_ui import box
from adafruit_display_text import label

BLACK=0x000000
WHITE=0xFFFFFF

#candies manages the candies display in the game
#it needs access to the display group to draw on, dpad for control
#and game data structure
class candies:
    def __init__(self, group, dpad, game):
        self.group=group
        self.dpad=dpad
        self.game=game
        #set initial position
        self.x=0
        self.y=0

        #Create the title in black text on the existing white header bar
        self.header=label.Label(terminalio.FONT,text="Candy, Game 0", color=BLACK, x=8, y=8)
        self.group.append(self.header)

        #create a layout of all the candies using a sprite table
        candy_sheet, palette = adafruit_imageload.load("assets/candies.bmp",bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.candy_grid = displayio.TileGrid(candy_sheet, pixel_shader=palette,
            width=13, height=3,
            tile_width=12, tile_height=16)
        self.candy_group=displayio.Group(y=15)
        self.candy_group.append(self.candy_grid)
        self.group.append(self.candy_group)

        #create a hidden detail overlay that is shown when the d-pad is pressed
        self.details=displayio.Group(x=8,y=4)
        self.details.hidden=True
        self.details.append(box(112,56,WHITE,0,0))
        self.details.append(box(110,54,BLACK,1,1))
        self.detail_label=label.Label(terminalio.FONT,text="About", color=WHITE, x=4, y=8)
        self.details.append(self.detail_label)
        self.group.append(self.details)

        #lay out all the cards, and set the initial position 
        self.set_cards()
        #highlight the currently selected card
        self.candy_grid[self.x,self.y]+=1


    def set_cards(self):
        #update header based on current game number
        self.header.text="Candy, game # " + str(self.game.game_num)
        #new data structure. todo Need to clarify x,y to type,candy mapping.
        #for row,candytype in enumerate(self.game.candies):
        for row,candytype in enumerate(self.game.candies.values()):
        #for candytype,candies in self.game.candies.items():
            if candytype["updated"]==True:
                candytype["updated"]=False
                self.x=0
                self.y=row
                count=0
                #show unknown cards
                for candy in candytype["unknown"]:
                    self.candy_grid[count,row]=7
                    count+=1
                #show known cards
                #todo: update images
                for candy in candytype["known"]:
                    self.candy_grid[count,row]=1
                    count+=1
                candytype["count"]=count
                for i in range(count,13):
                    self.candy_grid[i,row]=0
                #if solved, indicate it
                if len(candytype["unknown"])==1:
                    self.candy_grid[0,row]=9

    #process inputs and changes to state
    def update(self):
        #show grid
        self.candy_group.hidden=False
        #un-highlight current candy
        self.candy_grid[self.x,self.y]-=1
        #get the right candy for printing...
        candytype=self.game.candies[list(self.game.candies.keys())[self.y]]
        #this checks for candy updates
        self.set_cards()
        if self.dpad.u.fell:
            #pressing u at the top of the screen goes to trade
            if self.y==0:
                self.candy_grid[self.x,self.y]+=1
                return "trade"
            #otherwise just moves the cursor up
            self.y -=1
            candytype=self.game.candies[list(self.game.candies.keys())[self.y]]
            self.x=min(self.x,candytype["count"]-1)
        if self.dpad.d.fell:
            #pressing d at the bottom goes to sleep
            if self.y==2:
                self.candy_group.hidden=True
                self.details.hidden=True
                self.candy_grid[self.x,self.y]+=1
                return "sleep"
            #otherwise just moves the cursor down
            self.y +=1
            candytype=self.game.candies[list(self.game.candies.keys())[self.y]]
            self.x=min(self.x,candytype["count"]-1)
        if self.dpad.l.fell:
            #l at the left goes back to home
            if self.x==0:
                self.candy_group.hidden=True
                self.details.hidden=True
                self.candy_grid[self.x,self.y]+=1
                return "home"
            self.x -=1
        if self.dpad.r.fell:
            #r and the right goes around to settings
            if self.x==candytype["count"]-1:
                self.candy_group.hidden=True
                self.details.hidden=True
                self.candy_grid[self.x,self.y]+=1
                return "settings"
            self.x+=1
        if self.dpad.x.fell:
            #x shows or hides details
            self.details.hidden=not self.details.hidden
        #highlight the current selected candy
        self.candy_grid[self.x,self.y]+=1
        #get the right candy for printing...
        candytype=self.game.candies[list(self.game.candies.keys())[self.y]]
        all_candies=list(candytype["unknown"].items())+list(candytype["known"].items())
        (candy,informant)=all_candies[self.x]
        if self.game.unsolved==0:
                self.detail_label.text=self.game.solution_string
        elif informant=="":
            if len(candytype["unknown"])==1:
                self.detail_label.text="Attribution!\nIt was\n"+candy
            else:
                self.detail_label.text="Could've been\n"+candy
        elif informant==self.game.myname:
            self.detail_label.text="I know it wasn't\n"+candy
        else:
            self.detail_label.text=informant+"\nknows it wasn't\n"+candy
        return "candies"
