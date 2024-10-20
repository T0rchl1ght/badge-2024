#!/usr/bin/python3
import random
import os
import sys
import binascii
import adafruit_rsa
import json
from math import ceil

#this should do all the event-specific stuff
# todo: move candies and badge count to config file somewhere?
# todo: regenerate signatures if a new key was generated
# todo: make sure there's space for badge ID's in signatures dictionary
# todo: integrate with flash.py

candies=["Sour Patch Kids","Haribo Gummies","Smarties","Reese's Cups","Twix","Snickers"]
badge_count=20
hash_method="SHA-256"

#if keys are present, load them. if not, generate them
try:
    with open("priv.json", "r") as f:
        private_obj = json.loads(f.read())
        private_key=adafruit_rsa.PrivateKey(*private_obj["private_key_arguments"])
        public_key=adafruit_rsa.PublicKey(private_key.n, private_key.e)
    print("Keys loaded from priv.json\n")
except Exception as e:
    if input("no keys found, generate them? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    #remove all other config files, or set flag?
    print("Generating new keys: ",e)
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
    print("seed loaded from seed.txt\n")
except Exception as e:
    if input("no random seed found, generate one? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    print("Choosing new random seed: ")
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
    print("candies loaded from candies.json\n")
except Exception as e:
    if input("no candy signatures found, generate them? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)
    print("generating candy signatures:")
    candy_count=ceil(badge_count/len(candies))
    for i in range(candy_count):
        for candy in candies:
            unique_candy=candy + " #" + str(i)
            signatures[unique_candy]=str(binascii.b2a_base64(adafruit_rsa.sign(unique_candy.encode(), private_key, hash_method)))
    with open("candies.json", "w") as f:
        f.write(json.dumps(signatures))
    #print(signatures)


assignments={}
# if assignments are present, load them. If not, generate them.
try:
    with open("assignments.json", 'r') as f:
        assignments = json.loads(f.read())
    print("assignments loaded from assignments.json\n")
except Exception as e:
    if input("no prior assignments found, start from scratch? 'yes' to continue, anything else to quit\n") != "yes":
        exit(1)

allcandies=list(signatures.keys())
# now, as part of flash.py write this to mountpoint/id.json
for sn in ["1","2","3","4","5","4","3"]:
    if sn not in assignments:
        print("adding"+str(sn))
        print(len(assignments))
        assignments[sn]=allcandies[len(assignments)]
    with open("id"+sn+".json","w") as f:
        f.write(json.dumps({'name': '', 'candy': assignments[sn], 'signature': signatures[assignments[sn]]}))

with open("assignments.json", 'w') as f:
    f.write(json.dumps(assignments))

