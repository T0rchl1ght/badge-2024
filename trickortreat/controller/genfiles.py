#!/usr/bin/python3
import random
import os
import sys
import binascii
import adafruit_rsa
import json
from math import ceil, log10
import pyudev
import time
import subprocess
from threading import Thread
import time
import hashlib


#this should do all the event-specific stuff
# todo: regenerate signatures if a new key was generated
# todo: parameterize the file load/unload/generate

candies=["Sour Patch Kids","Haribo Gummies","Smarties","Reese's Cups","Twix","Snickers"]
badge_count=900  #overestimate this! Actually, maybe it shouldn't be settable? maybe dynamic? hmm.
hash_method="SHA-256"

#if keys are present, load them. if not, generate them
try:
    with open("priv.json", "r") as f:
        private_obj = json.loads(f.read())
        private_key=adafruit_rsa.PrivateKey(*private_obj["private_key_arguments"])
        public_key=adafruit_rsa.PublicKey(private_key.n, private_key.e)
    print("\n1. Prior keys loaded from priv.json.")
except Exception as e:
    if input("\nNo keys found, generate them? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    #remove all other config files, or set flag?
    print("1. Generating new keys...")
    (public_key, private_key) = adafruit_rsa.newkeys(512)
    public_obj = {"public_key_arguments": [public_key.n, public_key.e]}
    private_obj = { "private_key_arguments": [private_key.n, private_key.e,
                    private_key.d, private_key.p, private_key.q]}

    #probably should remove this since it's uncessessary and redundant to priv.json
    with open("pub.json", "w") as f:
        f.write(json.dumps(public_obj))

    with open("../badge/pub.json", "w") as f:
        f.write(json.dumps(public_obj))

    with open("priv.json", "w") as f:
        f.write(json.dumps(private_obj))
    print(private_key)

# check for seed, if not present, set the random seed so that game files are deterministic (not used in trick or treat)
try:
    with open("seed.txt", 'r') as file:
        seed = file.read()
        random.seed(seed)
    print("\n2. Prior seed loaded from seed.txt.")
except Exception as e:
    if input("\nNo random seed found, generate one? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    print("2. Choosing new random seed... ")
    seed = random.randrange(sys.maxsize)
    rng = random.Random(seed)
    f=open("seed.txt", "w")
    f.write(str(seed))
    f.close
    print("seed:", seed)


signatures={}

# if signatures are present, load them. If not, generate them.
try:
    with open("candies.json", 'r') as f:
        signatures = json.loads(f.read())
    print("\n3. Prior candies loaded from candies.json.")
except Exception as e:
    if input("\nNo candy signatures found, generate them? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    print("3. Generating new candy signatures..")
    candyCount=ceil(badge_count/len(candies))
    maxCandy=10**ceil(log10(candyCount))-1
    for i in range(candyCount):
        for candy in candies:
            unique_candy=candy + " #" + str(maxCandy-i)
            signatures[unique_candy]=str(binascii.b2a_base64(adafruit_rsa.sign(unique_candy.encode(), private_key, hash_method)))
    with open("candies.json", "w") as f:
        f.write(json.dumps(signatures))
    #print(signatures)


assignments={}
# if assignments are present, load them. If not, generate them.
try:
    with open("assignments.json", 'r') as f:
        assignments = json.loads(f.read())
    print("\n4. Prior assignments loaded from assignments.json.")
except Exception as e:
    if input("\nNo prior assignments found, start from scratch? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    print("4. New assignments log ready...")

allcandies=list(signatures.keys())

print("\nKeys, candies, and signatures loaded. Entering flashing mode. \n\nPlug in some badges!!\n")

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
circuitpy="adafruit-circuitpython-seeeduino_xiao_rp2040-en_US-9.1.4.uf2"
rpi_nuke="flash_nuke.uf2"
cpy_nuke="code.py"
gamefiles="../badge/*"

# write the correct id.json file for this badge serial number to the indicated destination
def registerserial(sn,dest):
    # if a new serial, assign the next candy
    if sn not in assignments:
        #todo: handle overflow here - more than the max # of badges seen!
        candyid=allcandies[len(assignments)]
        print(sn+" now assigned to give out "+candyid)
        assignments[sn]=candyid
    else:
        print(sn+" was already assigned "+assignments[sn])

    # always write out to destination
    with open(dest,"w") as f:
        f.write(json.dumps({'name': '', 'candy': assignments[sn], 'signature': signatures[assignments[sn]]}))

    # update our database
    with open("assignments.json", 'w') as f:
        f.write(json.dumps(assignments))

# node is a badge that was just plugged in. Mount it and return mount point.
def mountnode(node):
    subprocess.run("pmount "+node,shell=True)
    cmd='mount | grep '+node+' | cut -d " " -f 3'
    mountpoint=str(subprocess.check_output(cmd,shell=True),'UTF-8').strip()
    #print(node," was mounted at ",mountpoint)
    return mountpoint

# unmount the badge at this mount point
def umountpoint(mountpoint):
    cmd="sync -d "+mountpoint+" && pumount "+mountpoint
    subprocess.run(cmd,shell=True)
    #print(mountpoint, " unmounted - unplug it")

# copy this file from the badge at this mount point to a unique file locally:
def copyfromdevice(file, mountpoint):
    src=mountpoint+"/"+file
    dest="-".join([time.strftime("%Y%m%d-%H%M%S-"),device.get('ID_SERIAL_SHORT'),file])
    #print("copying from ", src, "to", dest)
    cmd="cp -Lr "+src+" "+dest
    subprocess.run(cmd,shell=True)
    return dest

# copy this file to the badge at this mount point 
def copytodevice(file, mountpoint):
    #print("copying ", file, " to ", mountpoint)
    cmd="cp -Lr "+file+" "+mountpoint+"/ && sync -d "+mountpoint
    subprocess.run(cmd,shell=True)

# copy game files to a badge with circuitpython loaded
def mkcpy(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)

    if mountpoint == "":
        raise Exception("empty mountpoint, would delete your system!!\n")
    sn=0
    sn=device.get('ID_SERIAL_SHORT')
    print(sn)

    # erase the existing filesystem if any
    # a better way might be to copy over code.py with storage.erase_filesystem()
    cmd="rm -rf "+mountpoint+"/*"
    subprocess.run(cmd,shell=True)

    #copy game code to badge
    copytodevice(gamefiles, mountpoint)

    #write the unique id.json to the device
    registerserial(sn,mountpoint+"/id.json")
    
    #clean up and report
    umountpoint(mountpoint)
    print("CPY #"+sn+" took "+str(time.time()-start)+"s")

# copy circuitpython to a blank rpi badge
def mkrpi(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(circuitpy,mountpoint)
    umountpoint(mountpoint)
    print("RPI took "+str(time.time()-start)+"s\n")

# wipe flash on a blank rpi badge (which may still have file fragments in flash)
def nukerpi(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(rpi_nuke,mountpoint)
    umountpoint(mountpoint)
    print("Nuking RPI took "+str(time.time()-start)+"s\n")

# reboot badge in rpi uf2 mode for nukerpi
def nukecpy(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(cpy_nuke,mountpoint)
    umountpoint(mountpoint)
    print("Nuking CPY took "+str(time.time()-start)+"si\n")


rpicount=0
cpycount=0
nukemode=False
if len(sys.argv)==2 and sys.argv[1] == "nuke":
    nukemode=True
    print("starting in nuke mode!! next device will get wiped!")

checkmode=False
if len(sys.argv)==2 and sys.argv[1] == "check":
    checkmode=True
    print("starting in checkout mode!")


# listen for device actions
for device in iter(monitor.poll, None):
    if device.action == 'add':
        # a device has been plugged in. Get it's name and do something to it
        label=device.get('ID_FS_LABEL')
        if label=="RPI-RP2":
            if nukemode:
                # the badge booted in uf2 mode and we want to nuke it with a uf2 that will zero all of flash
                print("Nuking flash on RPI at",device.device_node,"\n")
                nukerpi(device)
                nukemode=False
                continue
            # the badge is in uf2 mode, and we're just going to fork a thread to flash it with circuitpython
            rpicount+=1
            print("RPI #",str(rpicount),"\n")
            Thread(target=mkrpi, args=(device,)).start()
        if label=="CIRCUITPY":

            if checkmode:   #jjf put all this in a separate function checkcandy(device) 
                mountpoint=mountnode(device.device_node)
                copyfromdevice("id.json",mountpoint)
                copyfromdevice("candies.json",mountpoint)
                assignedCandyLocation="candies.json"        #jjf this is already loaded in allcandies{}
                ledgerLocation=mountpoint+'/candies.json'     #jjf put this assignment up near gamefiles
                with open(assignedCandyLocation,"r") as f:
                    assignedCandyData=json.load(f)


#jjf check if file exists before opening
#also, better to copy it locally so we can data horde, and not trigger restarts on badge by keeping the file open for a long time.
#i added copyfromdevice above; I'd recommend calling that then opening the local filename it returns.
                with open(ledgerLocation,"r") as f:        
                    badgeCandyData=json.load(f)


                umountpoint(mountpoint)
                    
#jjf need to umountpoint when done with the badge


                candy_counter = {}
                unique_signatures = set()

                for badgeCandy, badgeSignature in badgeCandyData.items():   
                    valid=False
                    for assignedCandy, assignedSignature in assignedCandyData.items():
#jjf 2 loops makes this an n^2 operation. Take advantage of the dictionary - allcandies.get(assignedCandy) 
# will return the assigned signature or None if there isn't one. you can compare that to badgeSignature
                        if ((badgeCandy == assignedCandy) & (badgeSignature == assignedSignature)):
                            # Extract the candy name without the increment (e.g., "Sour Patch Kids" instead of "Sour Patch Kids #1")
                            candy_name = badgeCandy.rsplit(' ', 1)[0]

                            # Update the candy count
# jjf candies[] contains all the unique candies - candycounter=dict.fromkeys(candies,0) will initialize them all to 0
                            if candy_name not in candy_counter:
                                candy_counter[candy_name] = 0
                            candy_counter[candy_name] += 1      #jjf note that this will count duplicate signatures as more candy

                            # Check if the signature is unique and add it to the set if it is
                            if badgeSignature not in unique_signatures:
                                unique_signatures.add(badgeSignature)
                                print(f"Candy: {badgeCandy}\nSignature: {badgeSignature}\n")
                                valid = True
                            else:
                                print(f"Duplicate signature found for {badgeCandy} and ignored.\n")
                    if valid == False:
                        print(f"{badgeCandy} seemed to be invalid...")

                # Print the candy counts
                print("\nCandy Collection Summary:")            #jjf would be great to add their name here
                for candy, count in candy_counter.items():
                    print(f"{candy}: {count}")

#jjf print some when done to make the output more clear and differentiate it from the last one
#jjf add a prompt to tell them to insert another powered-on badge - if the badge is battery powered but asleep - nothing will happen
            
                continue
            if nukemode:
                # badge running circuitpython and we want to reboot it in uf2 mode to nuke
                print("Nuking flash on CPY at",device.device_node,"\n")
                nukecpy(device)
                #need to nuke RP2 after this
                #nukemode=False
                continue
            # a badge running circutpython is plugged in - fork a thread to copy game files over
            cpycount+=1
            print("CPY #",str(cpycount))
            Thread(target=mkcpy, args=(device,)).start()
        if label=="CLEAR":
            # plugging in a usb drive with the volume label "CLEAR" will pumount all pmounted devices
            cmd="ls -lah /media/"
            subprocess.run(cmd,shell=True)
            print("unmounting\n")
            for filename in os.scandir("/media/"):
                umountpoint(filename.path)
                print(filename)
            subprocess.run(cmd,shell=True)
        if label=="NUKE":
            # plugging in a usb drive with the volume label "NUKE" will completely zero the flash of the next badge found
            nukemode=True
            print("Nuke mode enabled- next badge will get flash wiped first\n")
