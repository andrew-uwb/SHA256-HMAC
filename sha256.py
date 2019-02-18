#!/usr/bin/python3
import sys
from bitstring import BitArray

class sha256:
    
    def __init__(self):
        #Stores the list of K values (the first 32 bits of the fractional parts
        #of the cube roots of the first 64 prime numbers
        self.kValues = list()
        self.setKValues()

        #Variable to store the current state of the hash
        self.currentHash = BitArray()
                
    #This function hashes the given message.
    def hash(self, msgToHash):
        
        #On starting a new hash, make sure the current hash is empty
        self.currentHash = BitArray()
        
        #Add buffer to the message
        message = self.addBuffer(msgToHash)
        position = 0
        #Hash the message block by block
        while (position < message.length):
            #Isolate the next 512-bit segment of the message and hash it
            nextSegment = message[position:(position + 512)]
            #hashRound is where the hashing is actually done for each block
            self.hashRound(nextSegment)

            position = position + 512
        
        #Return the current hash
        return self.currentHash
            
         
    #This function adds the initial buffer to the message.    
    def addBuffer(self, inputBits):
        
        msgLength = inputBits.length
        
        lengthMod = (msgLength % 512)
        
        #Want to buffer to a length where the length mod 512 = 448
        #That way adding the 64 bit length ensures the length mod 512 = 0
        amtToBuffer = 448 - lengthMod
        #Even if exactly divisible, should always buffer
        if (amtToBuffer <= 0):
            amtToBuffer = amtToBuffer + 512
        
        #First bit in the buffer is 1, everything else is 0    
        inputBits.append(BitArray(bin='1'))
        amtToBuffer = amtToBuffer - 1
        inputBits.append(BitArray(uint=0,length=amtToBuffer))
            
        #After buffer, add the length (64 bits)    
        inputBits.append(BitArray(uint=msgLength,length=64))
            
        return inputBits
        
    def hashRound(self, segment):
        
        #Initialize word list as blank list
        wordList = list()
        
        #Create first 16 words of 32 bits each by splitting up this 512-bit block
        for x in range(0,16):
            wordList.append(segment[(32*x):(32*x + 32)])
            
        #Words 17-64 are created by formula
        for x in range(16,64):
            #Each word is created by performing functions on previous words in the list
            nextWord = self.moduloAddition(self.lowerSigmaOne(wordList[x - 2]),
                                           wordList[x - 7],
                                           self.lowerSigmaZero(wordList[x - 15]),
                                           wordList[x - 16])            
            wordList.append(nextWord)
        
        #If current hash is empty (in other words, this is the first pass through) then 
        #set the initial values to the first 32 bits of the fractional parts of the square roots of 
        #the first eight prime numbers.
        if (self.currentHash.length == 0):
            a = BitArray('0x6a09e667')
            b = BitArray('0xbb67ae85')
            c = BitArray('0x3c6ef372')
            d = BitArray('0xa54ff53a')
            e = BitArray('0x510e527f')
            f = BitArray('0x9b05688c')
            g = BitArray('0x1f83d9ab')
            h = BitArray('0x5be0cd19')
            self.currentHash = a + b + c + d + e + f + g + h
        #Otherwise load values a-h with the 8 32-bit words of the current hash.     
        else:
            a = self.currentHash[0:32]
            b = self.currentHash[32:64]
            c = self.currentHash[64:96]
            d = self.currentHash[96:128]
            e = self.currentHash[128:160]
            f = self.currentHash[160:192]
            g = self.currentHash[192:224]
            h = self.currentHash[224:256]
        
        #Do 64 rounds of hashing
        for x in range(0,64):
            
            #Calculate Function T1
            tOne = self.moduloAddition(h,
                                       self.upperSigmaOne(e),
                                       self.chFunction(e, f, g),
                                       self.kValues[x],
                                       wordList[x])
            
            #Calculate Function T2
            tTwo = self.moduloAddition(self.upperSigmaZero(a),
                                       self.majFunction(a, b, c))
            
            #Swap values
            h = g
            g = f
            f = e
            e = self.moduloAddition(d, tOne)
            d = c
            c = b
            b = a
            a = self.moduloAddition(tOne, tTwo)
            
            #testOutput.write(str(x) + " " + a.hex + " " + b.hex + " " + c.hex + " " + d.hex + 
            #                 " " + e.hex + " " + f.hex + " " + g.hex + " " + h.hex + '\n')
        
        #Calculate the next hash by adding values from new rounds to the current hash
        a = self.moduloAddition(a,self.currentHash[0:32])
        b = self.moduloAddition(b,self.currentHash[32:64])
        c = self.moduloAddition(c,self.currentHash[64:96])
        d = self.moduloAddition(d,self.currentHash[96:128])
        e = self.moduloAddition(e,self.currentHash[128:160])
        f = self.moduloAddition(f,self.currentHash[160:192])
        g = self.moduloAddition(g,self.currentHash[192:224])
        h = self.moduloAddition(h,self.currentHash[224:256])
        
        #Update current hash
        self.currentHash = a + b + c + d + e + f + g + h
            
    
    #Takes in any number of bit strings and does modulo 2^32 addition on them        
    def moduloAddition(self, *args):
        result = 0
        #print("Modulo addition")
        for nextArray in args:
        #    print(nextArray.uint)
            result = result + nextArray.uint
            
        result = result % (2**32)
        
        return BitArray(uint=result,length=32)
            
            
    #Maj(X,Y,Z) = (X AND Y) XOR (X AND Z) XOR (Y AND Z)    
    def majFunction(self, xInput, yInput, zInput):
        
        output = (xInput & yInput) ^ (xInput & zInput) ^ (yInput & zInput)
        return output
    
    #Ch(X,Y,Z) = (X AND Y) XOR ((COMPLEMENT X) AND Z)    
    def chFunction(self, xInput, yInput, zInput):
        
        output = (xInput & yInput) ^ (~xInput & zInput)
        return output
       
    #RotR(X,2) XOR RotR(X,13) XOR RotR(X,22)    
    def upperSigmaZero(self, xInput):
        
        xor1 = BitArray(xInput)
        xor2 = BitArray(xInput)
        xor3 = BitArray(xInput)
        
        xor1.ror(2)
        xor2.ror(13)
        xor3.ror(22)
        
        output = xor1 ^ xor2 ^ xor3
        
        return output
    
    #RotR(X,6) XOR RotR(X,11) XOR Rotr(X,25)    
    def upperSigmaOne(self, xInput):
        
        xor1 = BitArray(xInput)
        xor2 = BitArray(xInput)
        xor3 = BitArray(xInput)
        
        xor1.ror(6)
        xor2.ror(11)
        xor3.ror(25)
        
        output = xor1 ^ xor2 ^ xor3
        
        return output
    
    #RotR(X,7) XOR RotR(X,18) XOR ShR(X,3)
    def lowerSigmaZero(self, xInput):
        
        termOne = BitArray(xInput)
        termTwo = BitArray(xInput)
        termThree = xInput >> 3
        
        termOne.ror(7)
        termTwo.ror(18)
        
        #print(termOne.bin)
        #print(termTwo.bin)
        #print(termThree.bin)
        
        output = termOne ^ termTwo ^ termThree
        
        #print(output.bin)
        
        return output
    
    #RotR(X,17) XOR RotR(X,19) XOR ShR(X,10)
    def lowerSigmaOne(self, xInput):
        
        termOne = BitArray(xInput)
        termTwo = BitArray(xInput)
        termThree = xInput >> 10
        
        termOne.ror(17)
        termTwo.ror(19)
        
        #print(termOne.bin)
        #print(termTwo.bin)
        #print(termThree.bin)
        
        output = termOne ^ termTwo ^ termThree
        
        #print(output.bin)
        
        return output
    
    #This function sets a list consisting of the first 32 bits of the fractional parts 
    #of the cube roots of the first 64 prime numbers
    def setKValues(self):
        
        self.kValues = list()
        self.kValues.append(BitArray('0x428a2f98'))
        self.kValues.append(BitArray('0x71374491'))
        self.kValues.append(BitArray('0xb5c0fbcf'))
        self.kValues.append(BitArray('0xe9b5dba5'))
        self.kValues.append(BitArray('0x3956c25b'))
        self.kValues.append(BitArray('0x59f111f1'))
        self.kValues.append(BitArray('0x923f82a4'))
        self.kValues.append(BitArray('0xab1c5ed5'))
        
        self.kValues.append(BitArray('0xd807aa98'))
        self.kValues.append(BitArray('0x12835b01'))
        self.kValues.append(BitArray('0x243185be'))
        self.kValues.append(BitArray('0x550c7dc3'))
        self.kValues.append(BitArray('0x72be5d74'))
        self.kValues.append(BitArray('0x80deb1fe'))
        self.kValues.append(BitArray('0x9bdc06a7'))
        self.kValues.append(BitArray('0xc19bf174'))
        
        self.kValues.append(BitArray('0xe49b69c1'))
        self.kValues.append(BitArray('0xefbe4786'))
        self.kValues.append(BitArray('0x0fc19dc6'))
        self.kValues.append(BitArray('0x240ca1cc'))
        self.kValues.append(BitArray('0x2de92c6f'))
        self.kValues.append(BitArray('0x4a7484aa'))
        self.kValues.append(BitArray('0x5cb0a9dc'))
        self.kValues.append(BitArray('0x76f988da'))
        
        self.kValues.append(BitArray('0x983e5152'))
        self.kValues.append(BitArray('0xa831c66d'))
        self.kValues.append(BitArray('0xb00327c8'))
        self.kValues.append(BitArray('0xbf597fc7'))
        self.kValues.append(BitArray('0xc6e00bf3'))
        self.kValues.append(BitArray('0xd5a79147'))
        self.kValues.append(BitArray('0x06ca6351'))
        self.kValues.append(BitArray('0x14292967'))
        
        self.kValues.append(BitArray('0x27b70a85'))
        self.kValues.append(BitArray('0x2e1b2138'))
        self.kValues.append(BitArray('0x4d2c6dfc'))
        self.kValues.append(BitArray('0x53380d13'))
        self.kValues.append(BitArray('0x650a7354'))
        self.kValues.append(BitArray('0x766a0abb'))
        self.kValues.append(BitArray('0x81c2c92e'))
        self.kValues.append(BitArray('0x92722c85'))
        
        self.kValues.append(BitArray('0xa2bfe8a1'))
        self.kValues.append(BitArray('0xa81a664b'))
        self.kValues.append(BitArray('0xc24b8b70'))
        self.kValues.append(BitArray('0xc76c51a3'))
        self.kValues.append(BitArray('0xd192e819'))
        self.kValues.append(BitArray('0xd6990624'))
        self.kValues.append(BitArray('0xf40e3585'))
        self.kValues.append(BitArray('0x106aa070'))
        
        self.kValues.append(BitArray('0x19a4c116'))
        self.kValues.append(BitArray('0x1e376c08'))
        self.kValues.append(BitArray('0x2748774c'))
        self.kValues.append(BitArray('0x34b0bcb5'))
        self.kValues.append(BitArray('0x391c0cb3'))
        self.kValues.append(BitArray('0x4ed8aa4a'))
        self.kValues.append(BitArray('0x5b9cca4f'))
        self.kValues.append(BitArray('0x682e6ff3'))
        
        self.kValues.append(BitArray('0x748f82ee'))
        self.kValues.append(BitArray('0x78a5636f'))
        self.kValues.append(BitArray('0x84c87814'))
        self.kValues.append(BitArray('0x8cc70208'))
        self.kValues.append(BitArray('0x90befffa'))
        self.kValues.append(BitArray('0xa4506ceb'))
        self.kValues.append(BitArray('0xbef9a3f7'))
        self.kValues.append(BitArray('0xc67178f2'))
         
#This is the end of the SHA256 class         

if __name__=='__main__':
    
    #Take in password and keyfile from command line         
    pwd = sys.argv[1]
    keyfile = sys.argv[2]

    #Object to hash the password
    hasher = sha256()
    #Create a bit array from the password
    pwdBits = BitArray(pwd.encode("utf8"))

    #Hash the password
    hashedPwd = hasher.hash(pwdBits)

    #Write out the resulting hash to the keyfile
    outfile = open(keyfile, 'w')
    outfile.write(hashedPwd.hex)
    outfile.close