# Currently only supports one key slot

from Crypto.Cipher import AES
from pbkdf2 import PBKDF2
from os import urandom
from struct import pack, unpack
from math import ceil
from driver import Block, diskSim, BLOCK_SIZE
from strings import hexify
from xor import xor

class diskEncrypt:
    def __init__(self):
        self.sim = diskSim()
        self.disk = None
        self.mode = "XTS"
        self.numKeyslots = 8
        self.ksLength = 64
        self.masterKey = None

    def setMode(self, mode):
        raise NotImplementedError

    def getMode(self, mode):
        return self.mode

    def __xex(self, data, start, size):
        E = AES.new(self.masterKey, AES.MODE_ECB)
        c = ""

        i = start
        for j in range(BLOCK_SIZE):
            x = xor(E.encrypt(pack(">QQ", 0, i)), 2**j)
            c += xor(xor(E.encrypt(data[j:j + 16], x)), x)

        return c

    def read(self, blockNum, size):
        E = AES.new(self.masterKey, AES.MODE_ECB)
        c = ""

        i = blockNum 
        block = Block()
        self.sim.readBlock(self.disk, i, block)
        data = block.getData()

        for j in range(BLOCK_SIZE()):
            x = xor(E.encrypt(pack(">QQ", 0, i)), str(2**j))
            c += xor(xor(E.decrypt(data[j:j + 16]), x), x)

        return c

    def write(self, data, blockNum, size):
        #size = int(ceil(float(size) / BLOCK_SIZE()))
        #blockNum = self.sim.freeBlock(self.disk, size)

        E = AES.new(self.masterKey, AES.MODE_ECB)
        c = ""

        i = blockNum
        print(len(data))
        for j in range(BLOCK_SIZE() + 1, 16):
            x = xor(E.encrypt(pack(">QQ", 0, i)), str(2**j))
            c += xor(xor(E.encrypt(data[j:j + 16]), x), x)

        block = Block(c)
        self.sim.writeBlock(self.disk, i, block)
        return 0

    # Pads data up to BLOCK_SIZE.
    def __zeroPadBlock(self, dataSize):
        return '\x00' * (BLOCK_SIZE() - dataSize)

    # Creates a new encrypted disk. Adds necessary header information and 
    # formats disk. Creates master key and encrypts it with PBKDF2.
    def createDisk(self, filename, diskSize, passwd):

        # Mount the disk. Add one extra block to store header.
        self.disk = self.sim.mountDisk(filename, diskSize + BLOCK_SIZE())
        if self.disk < 0:
            return -1

        iterations = 10000

        # Create new master key and digest.
        masterKey = urandom(16) # Master key for encrypting disk.
        mk_salt = urandom(32)
        mk_digest = PBKDF2(masterKey, mk_salt, iterations = iterations).read(16)

        # Create user key.
        salt = urandom(32)
        passwd_digest = PBKDF2(passwd, salt, iterations=iterations).read(16)
        encrypted_master_key = AES.new(passwd_digest, AES.MODE_ECB).encrypt(masterKey)
        key_slot = pack(">i", iterations) + salt + encrypted_master_key
        ks2 = "\x00" * (self.ksLength * (self.numKeyslots - 1)) # Future key slots.

        # Create block object to write to disk.
        test = pack(">i", iterations)
        data = mk_digest + mk_salt + pack(">i", iterations) + key_slot + ks2
        block = Block(data + self.__zeroPadBlock(len(data)))

        # Write header to disk.
        self.sim.writeBlock(self.disk, 0, block)

        # Write random data to rest of disk.
        for i in  range(1, (diskSize + BLOCK_SIZE()) / BLOCK_SIZE()):
            self.sim.writeBlock(self.disk, i, Block(urandom(BLOCK_SIZE())))

        return 0

    # Attempts to decrypt master key with |passwd| so that the disk can 
    # be mounted.
    def openDisk(self, filename, passwd):
        self.disk = self.sim.mountDisk(filename, 0)
        if self.disk < 0:
            return -2

        # Recover data from header.
        block = Block()
        if self.sim.readBlock(self.disk, 0, block) < 0:
            return -3

        header = block.getData()
        mk_digest = header[:16]
        mk_salt = header[16:48]
        iterations = unpack('>i', header[48:52])[0]
        ks = header[52:52 + self.ksLength]
        ks_iter = unpack(">i", ks[0:4])[0]
        ks_salt = ks[4:36]
        ks_digest = ks[36:52]

        # Attempt to decrypt master key.
        passwd_diget = PBKDF2(passwd, ks_salt, iterations=ks_iter).read(16)
        master_key_candidate = AES.new(passwd_diget, AES.MODE_ECB).decrypt(ks_digest)
        
        # Check if correct PBKDF2 digest if produced.
        if mk_digest != PBKDF2(master_key_candidate, mk_salt, iterations=iterations).read(16):
            return -4

        # Correct master key found, store it.
        self.masterKey = master_key_candidate
        return 0

    def closeDisk(self, filename):
        self.sim.unmountDisk(self.disk)
        self.masterKey = 0
