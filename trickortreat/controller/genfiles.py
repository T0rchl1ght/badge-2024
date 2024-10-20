#!/usr/bin/python3
import random
import os
import sys
import binascii
import adafruit_rsa
import json
from math import ceil

# number of variants to generate
working_dir = os.path.dirname(os.path.realpath(__file__))

hash_method="SHA-256"
candies=["Sour Patch Kids","Haribo Gummies","Smarties","Reese's Cups","Twix","Snickers"]
badge_count=20

try:
    with open("priv.json", "r") as f:
        private_obj = json.loads(f.read())
        private_key=adafruit_rsa.PrivateKey(*private_obj["private_key_arguments"])
        public_key=adafruit_rsa.PublicKey(private_key.n, private_key.e)
except Exception as e:
    print("Generating new keys: ",e)
    (public_key, private_key) = adafruit_rsa.newkeys(512)
    public_obj = {"public_key_arguments": [public_key.n, public_key.e]}
    private_obj = { "private_key_arguments": [private_key.n, private_key.e,
                    private_key.d, private_key.p, private_key.q]}

    f=open("pub.json", "w")
    f.write(json.dumps(public_obj))
    f.close()

    f=open("../badge/pub.json", "w")
    f.write(json.dumps(public_obj))
    f.close()

    f=open("priv.json", "w")
    f.write(json.dumps(private_obj))
    f.close()

print(public_key)
print(private_key)

# set the random seed so that game files are deterministic (not used in trick or treat)
try:
    with open("seed.txt", 'r') as file:
        seed = file.read()
        random.seed(seed)
except Exception as e:
    print("Choosing new random seed: ")
    seed = random.randrange(sys.maxsize)
    rng = random.Random(seed)
    f=open("seed.txt", "w")
    f.write(str(seed))
    f.close

print("seed:", seed)


signatures={}

try:
    with open("candies.json", 'r') as f:
        signatures = json.loads(f.read())
except Exception as e:
    print("generating candy signatures:",e)
    candy_count=ceil(badge_count/len(candies))
    for candy in candies:
        for i in range(candy_count):
            unique_candy=candy + " " + str(i)
            signatures[unique_candy]=str(binascii.b2a_base64(adafruit_rsa.sign(unique_candy.encode(), private_key, hash_method)))
    f=open("candies.json", "w")
    f.write(json.dumps(signatures))
    f.close()

print(signatures)

