from adafruit_ticks import ticks_ms
from adafruit_display_text import label
from fake_irda import FakeIRDA
from ssd1306_ui import box
import terminalio
from binascii import crc32,unhexlify,a2b_base64,b2a_base64
from adafruit_rsa import verify
from gc import collect
from time import sleep


BLACK=0x000000
WHITE=0xFFFFFF

#this manages the trading of data with others. Unlike the other views,
#this one is blocking during RX (though this could probably be fixed).
#This class manages the crc check to ensure valid data is tx/rx, but
#game.check_candy does the data structure validation and update
class trade:
    collect()
    state="transmitting"
    timeout=0

    def __init__(self, dpad, game, disp):
        # self.group=group
        self.dpad=dpad
        self.ir=FakeIRDA()
        self.game=game
        self.disp=disp

        """
        #draw a box over the screen with black text on top and white below
        self.group.append(box(112,64,WHITE,0,0))
        self.group.append(box(110,47,BLACK,1,16))
        self.header=label.Label(terminalio.FONT,text="trade", color=BLACK, x=4, y=8)
        self.group.append(self.header)
        self.details=label.Label(terminalio.FONT,text="transmitting", color=WHITE, x=12, y=24)
        self.group.append(self.details)
        """

        self.rxname=None
        self.rxcandy=None

    def update(self):
        #show trade page
        #self.group.hidden=False
        self.disp.setHeader("Trade")

        while True:
            #turn on the PHY to enable tx/rx
            self.ir.enablePHY()

            # Transmit state. Transmit the pre-calculated tx value
            if self.state == "transmitting":
                print("transmitting")
                self.disp.setText("tranmitting...")
                self.ir.writebytes(self.game.mytxval)
                #tx complete; prepare to rx. Clear buffer and set timeout
                self.ir.uart.reset_input_buffer()
                self.state="receiving"
                self.timeout=ticks_ms()+30000

            # receive state. listen until data received, then check it and proceed
            elif self.state == "receiving":
                if self.ir.ready(4):
                    print("incoming")
                    #4 bytes are in the queue - enough to get started. Get data
                    rxval=self.ir.readbytes()
                    print(f"RX: {rxval}")
                    
                    if self.game.check_candy(rxval):
#                    if rxval.count(',') == 3:
#                        self.rxname,self.rxcandy,self.rxsignature,chksum= rxval.split(',')
#                        #print(f"RX: {chksum}, {self.rxcandy}, {self.rxname},{self.rxsignature}\n\n")
#                        try:
#                            print("trying!")
#                            #check crc is valid.
#                            print(bytearray(hex(crc32(bytearray(",".join([self.rxname,self.rxcandy,self.rxsignature]),'utf8'))),'utf8'), chksum,"\n\n")
#                            chkval=bytearray(hex(crc32(bytearray(",".join([self.rxname,self.rxcandy,self.rxsignature]),'utf8'))),'utf8')
#                            if bytearray(hex(crc32(bytearray(",".join([self.rxname,self.rxcandy,self.rxsignature]),'utf8'))),'utf8') != chksum:
#                                print("[!] Invalid Checksum")
#                                self.state="error"
#                                self.disp.setText("receive error :(\n^ try again\nv cancel")
#                            #check signature
#                            elif verify(self.rxcandy.encode(),a2b_base64(self.rxsignature[1:]),self.game.pubkey):
#                                print("verified\n")
#                                #check that strings are not none
#                                if self.rxcandy is not None and self.rxname is not None and self.game.check_candy(self.rxcandy, self.rxname):
                        #if the candy was valid, move to responding
                        print("received")
                        self.state="responding"
                        sleep(.5)
                    else:
                    #if candy was invalid, we got an error
                    #todo: this should probably be retry since tx/rx is more robust now
                        print("receive error")
                        self.state="error"
                        self.disp.setText(["error try again or","check your game #","^ again    v cancel"])
#                        except Exception as e:
#                            print("we foiled the hackers!, ",e)
#                            self.state="error"
#                            self.disp.setText(["Bad Signature!","Ignoring cheap","forgery  ^  v"])
                #go to timeout if we've been waiting too long
                elif ticks_ms()> self.timeout:
                    print("timeout")
                    self.state="timeout"
                    self.disp.setText(["timeout :(","^ try again","v cancel"])
                #otherwise, show a timeout countdown
                else:
                    self.disp.setText("receiving{}".format((self.timeout - ticks_ms()) // 1000))
                    #print("nothing received yet",self.timeout,ticks_ms())

            #responding state. Send our candy one more time
            elif self.state == "responding":
                print("responding")
                self.disp.setText("responding")
                self.ir.writebytes(self.game.mytxval)
#                self.ir.writebytes(self.game.mytxval)
                #done responding. Go to success state
                self.state="success"
                print(self.rxname,"\nsaid it wasn't\n",self.rxcandy)
                self.disp.setText([
                    "{}".format(self.rxname),
                    "said it wasn't",
                    "{}".format(self.rxcandy)
                ])

            #success, timeout, and error states don't have any following action - just wait for buttons

            # process keypress
            self.dpad.update()
            # if down is pressed, return to where we came from
            retval=None
            if self.state=="solved" and self.dpad.pressed():
                 #if settext reult is true handle
                 print(self.game.solution_string)
                 self.disp.setText(["solved! Advance","to next game","in settings"])
                 if self.dpad.l.fell or self.dpad.r.fell:
                     retval="home"
                 elif self.dpad.l.fell:
                     retval="candies"
                 elif self.dpad.r.fell:
                     self.game.game_num=(self.game.game_num+1)%8
                     self.game.game_file="data/game"+str(self.game.game_num)+".csv"
                     self.game.read_candies()
                     retval="candies"
            elif self.dpad.d.fell:
                retval=0
            elif self.dpad.u.fell:
                self.state="transmitting"
            elif self.state=="success":
                if self.dpad.pressed(): retval=0
            if retval is not None:
                self.ir.disablePHY()
                self.state="transmitting"
                # self.group.hidden=True
                return retval
            # if u is pressed, restart the trade process
