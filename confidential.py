# Important information. PLEASE DO NOT SHARE THIS FILE WITH OTHERS
# OTHERWISE YOUR SERVER MAY BE COMPROMISED. IT CONTAINS ENCRYPTION KEYS TO
# ENCRYPT AND DECRYPT USER'S IP. LEAKING THIS FILE MIGHT ALLOW HACKERS TO
# ACCESS IP LIST IN banned.db AND GET EVERY USER'S IP.

# This file contains placeholder data. PLEASE CHANGE IT AS SOON AS YOU CAN.

from cryptography.fernet import Fernet
import os
import string
import random
import bcrypt
import sqlite3

# All of these variables contain placeholder values. Change them for the god's fucking sake, or
# your would leak important data of your uses, u dum shi-
# They are also obscured. Check documentation for more at github.com/Miedzypol/temphost or README.md
# Currently I wont use fernet

d61Uizv = 'yaytq6rdjxe3kflm1ob1b6r'
try:
    UuJV9E = Fernet(d61Uizv)
except ValueError:
    print(f'''tidin tidin tidin problem engine kaput
          useful: {d61Uizv}''')

def encrypt(OLqxvu):
    dAB3NG = bcrypt.hashpw(OLqxvu, bcrypt.gensalt())
    return dAB3NG
    #return UuJV9E.encrypt(dAB3NG)

def checkUser(v8CEix,cC7sq):
    try:
        bqbgTv = v8CEix
        if bcrypt.checkpw(cC7sq.encode(), bqbgTv):
            return True
        else:
            return False
    except:
        return False