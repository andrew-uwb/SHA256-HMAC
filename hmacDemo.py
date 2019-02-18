#!/usr/bin/python3
import os
import getpass

#Input user password that will be hashed with SHA256 and placed into keyfile.txt
passwd = getpass.getpass("Please enter a password: ")

#Input file with message that will be hashed using hmac functionality and placed into hmacoutput.txt:
fileInput = input("Enter a file to use for HMAC. (If blank, uses provided message.txt): ")

if (fileInput == ""):
    fileInput = 'message.txt'

#Install the Bitstring library
print("Checking for Python bitstring library...")
os.system('pip install bitstring')

#Install the PyCryptodomex library. This replaces the older pycrypto but can still exist alongside it.
print("Checking for Python Cryptodome library...")
os.system('pip install pycryptodomex')

print("Computing hash...")

#Step 1: Use sha256 to generate hash from password
os.system('python sha256.py ' + passwd + ' keyfile.txt')

print("Hash stored in keyfile.txt.")
print("Calculating HMAC from key in keyfile.txt and message in " + fileInput + "...")

#Step 2: Create HMAC using hash from step 1 as password
os.system('python hmac.py create keyfile.txt ' + fileInput + ' output.txt')

print("HMAC stored in output.txt")
print("Verifying HMAC against standard library...")

#Step 3: Verify the output from Step 2 against a standard library
os.system('python hmac.py verify keyfile.txt ' + fileInput + ' output.txt')
