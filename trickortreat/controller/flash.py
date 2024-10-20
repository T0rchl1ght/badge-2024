#!/bin/python3
import os
import pyudev
import time
import subprocess
from threading import Thread
import time
import hashlib

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
circuitpy="adafruit-circuitpython-seeeduino_xiao_rp2040-en_US-9.1.4.uf2"
rpi_nuke="flash_nuke.uf2"
cpy_nuke="code.py"
software="../badge/*"
#configs="../configs/data/"
#variants=50

def mountnode(node):
    subprocess.run("pmount "+node,shell=True)
    cmd='mount | grep '+node+' | cut -d " " -f 3'
    mountpoint=str(subprocess.check_output(cmd,shell=True),'UTF-8').strip()
    #print(node," was mounted at ",mountpoint)
    return mountpoint

def umountpoint(mountpoint):
    cmd="sync -d "+mountpoint+" && pumount "+mountpoint
    subprocess.run(cmd,shell=True)
    #print(mountpoint, " unmounted - unplug it")

def copytodevice(file, mountpoint):
    #print("copying ", file, " to ", mountpoint)
    cmd="cp -Lr "+file+" "+mountpoint+"/ && sync -d "+mountpoint
    subprocess.run(cmd,shell=True)

def mkcpy(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    if mountpoint == "":
        raise Exception("empty mountpoint, would delete your system!!\n")
    sn=0
    sn=device.get('ID_SERIAL_SHORT')
    #hash=hashlib.md5(sn.encode('utf-8'))
    #num=int.from_bytes(hash.digest(), 'big', signed=False)
    #variant = num % variants
    #config=ord(serial[-1])%50
    cmd="rm -rf "+mountpoint+"/*"
    subprocess.run(cmd,shell=True)
    copytodevice(software, mountpoint)
    #copytodevice(configs+str(variant)+"/*", mountpoint+"/data/")
    umountpoint(mountpoint)
    print("CPY #"+sn+" config #",variant," took "+str(time.time()-start)+"s\n")

def mkrpi(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(circuitpy,mountpoint)
    umountpoint(mountpoint)
    print("RPI took "+str(time.time()-start)+"s\n")

def nukerpi(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(rpi_nuke,mountpoint)
    umountpoint(mountpoint)
    print("Nuking RPI took "+str(time.time()-start)+"s\n")

def nukecpy(device):
    start=time.time()
    mountpoint=mountnode(device.device_node)
    copytodevice(cpy_nuke,mountpoint)
    umountpoint(mountpoint)
    print("Nuking CPY took "+str(time.time()-start)+"si\n")


rpicount=0
cpycount=0
nukemode=False

for device in iter(monitor.poll, None):
    if device.action == 'add':
        label=device.get('ID_FS_LABEL')
        if label=="RPI-RP2":
            if nukemode: 
                print("Nuking flash on RPI at",device.device_node,"\n")
                nukerpi(device)
                nukemode=False
                continue
            rpicount+=1
            print("RPI #",str(rpicount),"\n")
            Thread(target=mkrpi, args=(device,)).start()
        if label=="CIRCUITPY":
            if nukemode:
                print("Nuking flash on CPY at",device.device_node,"\n")
                nukecpy(device)
                #need to nuke RP2 after this
                #nukemode=False
                continue
            cpycount+=1
            print("CPY #",str(cpycount),"\n")
            Thread(target=mkcpy, args=(device,)).start()
        if label=="CLEAR":
            cmd="ls -lah /media/"
            subprocess.run(cmd,shell=True)
            print("unmounting\n")
            for filename in os.scandir("/media/"):
                umountpoint(filename.path)
                print(filename)
            subprocess.run(cmd,shell=True)
        if label=="NUKE":
            nukemode=True
            print("Nuke mode enabled- next badge will get flash wiped first\n")

