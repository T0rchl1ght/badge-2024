import circuitpython_csv
import gc
#from binascii import crc32
from binascii import crc32,a2b_base64
from json import loads
from adafruit_rsa import PublicKey

# this class contains all the data relevant to the game. It manages
# loading the data from files, updating it, and writing it back.
class game_data:
    # game_num=0  # set in __init__
    mycandy=None
    signature=""
    # myname=None # set in __init__ via call to read_myname()
    mytxval=None
    game_file="data/game1.csv"
    friends_file="data/friends.csv"

    #initialize all the data. Read all 3 files and load into memory
    def __init__(self,game_num=0):
        self.game_num=game_num
        self.read_name()
        self.read_friends()
        self.pubkey=self.read_pubkey()
        print(self.pubkey)
        self.game_file="data/game"+str(game_num)+".csv"
        self.read_candies()

    #check a candy, and if valid for this game, add it to the structure.
    def check_candy(self,newcandy,friend):
        #if we haven't met the friend before, a them to the list, and flush to disk
        if friend not in self.friends.keys():
            self.friends[friend]=[newcandy]
        # if we have, append the candy to the list of candies
        else:
            print(f"Friend {friend} already known, appending")
            #check for duplicate candy in this list
            if newcandy not in self.friends[friend]:
                self.friends[friend].append(newcandy)
        self.write_friends()
        #iterate over all candies. If we have the candy, mark it collected, log the friend,
        #flag it so the display knows to update it, and flush to disk
        match=False
        for typename,candytype in self.candies.items():
            if newcandy in candytype["known"]:
                print("candy already shared by ",candytype["known"][newcandy]," but thanks anyway "+friend)
                match=True
                break
            elif len(candytype["unknown"])>1 and newcandy in candytype["unknown"]:
                print("new candy!",newcandy)
                candytype["known"][newcandy]=friend
                del candytype["unknown"][newcandy]
                self.check_for_solution(typename,candytype)
                candytype["updated"]=True
                match=True
                break
        if match :
            self.write_candies()
            return newcandy
        return False

    #load name from file - if it's not there, set to unknown
    #note that we don't do the oob flow here because that needs
    #control of display we don't want in the data storage class.
    def read_name(self):
        try:
            with open("data/myname.txt",'r') as file:
                self.myname=file.readline().rstrip()
                print("hello",self.myname)
        except OSError:
            print("Error reading name from data/myname.txt")
            self.myname="unknown"

    # clear name and write to file
    def wipe_name(self):
        self.myname=""
        self.write_name()

    #open the name file and write out to it
    def write_name(self):
        try:
            with open("data/myname.txt", 'w') as fhandle:
                fhandle.write(self.myname)
        except OSError:
            print("Error writing name file")
            return False
        return True

    def check_for_solution(self,typename,candytype):
        if len(candytype["unknown"]) == 1:
            answer=list(candytype["unknown"].keys())[0]
            self.solution_string=self.solution_string.replace("["+typename+"]",answer)
            print(self.solution_string)
            self.unsolved-=1
            print("#unsolved: ", self.unsolved)
            if self.unsolved==0:
                print("full solution!!")

    #read csv file of candies for this game. Can be called again
    #to change to a different game number
    def read_candies(self):
        try:
            with open(self.game_file, 'r') as file:
                csv=circuitpython_csv.reader(file)
                #dict to hold candy types which hold candies
                self.candies={}
                #first value tells us what type of candy it is
                self.solution_string="#T used #A against #V"
                for row in csv:
                    if row[0] == "*":
                        #print(row)
                        self.mycandy=row[1]
                        #print(self.mycandy,row[2],self.signature)
                        #todo: this should be added to game files as row[2]
                        self.signature=a2b_base64(row[2])
                        self.signature=row[2]
                        #self.signature="none
                    elif row[0] == "#":
                        self.solution_string=row[1]
                        print(self.solution_string)
                    #make sure we have enough data
                    elif len(row) > 3:
                        status="unknown" if row[3]=="" else "known"
                        #if we haven't seen this candytype before, create the dict
                        if row[0] not in self.candies:
                            self.candies[row[0]]={"known":{},"unknown":{},"updated":True}
                        #and enter the candy into the dict
                        self.candies[row[0]][status][row[1]]=row[3]
            # count of unsolved categories
            self.unsolved=len(self.candies)
            # check for solutions, count unsolved categories
            for typename,candytype in self.candies.items():
                self.check_for_solution(typename,candytype)
                candytype["updated"]=True
            print("#unsolved: ", self.unsolved)

            print(self.candies)
            #add our candy to the table
            self.check_candy(self.mycandy,self.myname)
            #calculate the message we'll send when we trade.
            transmit_data=bytearray(",".join([self.myname,str(self.game_num),self.mycandy,str(self.signature)]),'utf8')
            #calculate CRC
            crc = hex(crc32(transmit_data))#[2:]
            #crc = str(crc32(transmit_data))
            #self.mytxval=transmit_data+crc
            self.mytxval=transmit_data+bytearray(","+crc,'utf8')
            print(f"{self.mytxval}")
        except OSError:
            print("Error reading from file:", self.game_file)

    #essentially 'resets' the current game, wiping all candies then adding yours back
    def wipe_candies(self):
        ## new candy structure
        for candytype in self.candies.values():
            for candy in candytype["known"]:
                candytype["unknown"][candy]=""
            candytype["known"]={}
            candytype["updated"]=True
        print(self.candies)
        self.check_candy(self.mycandy,self.myname)
        self.write_candies()

    #write candies csv to disk so it persists through power cycles
    def write_candies(self):
        #should be called every time we add a candy?
        try:
            ## new candy structure
            fhandle = open(self.game_file, 'w')
            fhandle.write("#,"+self.solution_string+"\n")
            for candytype in self.candies.keys():
                for candy in self.candies[candytype]["known"]:
                    print(candytype+","+candy+","+self.candies[candytype]["known"][candy])
                    fhandle.write(candytype+","+candy+",0,"+self.candies[candytype]["known"][candy]+"\n")
                for candy in self.candies[candytype]["unknown"]:
                    print(candytype+","+candy+",0,")
                    fhandle.write(candytype+","+candy+",0,"+"\n")
            print("*,"+str(self.mycandy))
            #tack on your candy at the end
            fhandle.write("*,"+str(self.mycandy)+","+self.signature)
            fhandle.close()
        except OSError:
            print("Error writing candies file:", self.game_file)
            return False
        return True

    def read_friends(self):
        try:
            self.friends={}
            with open(self.friend_file, 'r') as file:
                for row in circuitpython_csv.reader(file):
                    self.friends[row[0]]=row[1:]
            #print(self.friends)
        except OSError:
            print("Error reading from file:", self.friend_file)

    #clear list of friends except for yourself, and flush to disk
    def wipe_friends(self):
        self.friends=[[self.myname]]
        self.write_friends()

    def write_friends(self):
        try:
            fhandle = open(self.friend_file, 'w')
            for friend_name,friend in self.friends.items():
                fhandle.write(friend_name+","+",".join(friend))
                print(friend_name,",".join(friend))
                fhandle.write("\n")
        except OSError:
            print("Error writing friend file:", self.friend_file)
            return False
        return True

    def read_pubkey(self):
        with open("pub.json", "r") as f:
            pub_key_obj = loads(f.read())
        return PublicKey(*pub_key_obj["public_key_arguments"])

