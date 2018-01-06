from struct import pack, unpack

# Since Python does not have constants, define a function to return the block size.
def BLOCK_SIZE():
    return 4096

def diskError(e):
    raise NotImplementedError

class Block:
    def __init__(self, data = None):
        self.data = data

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

class diskSim:
    def __init__(self):
        self.openDisks = []
        self.diskSizes = {}
        self.freeBlocks = {}
        #self.mdSize = 8

    # Opens the file |filename| and uses the first |numBytes| of the file as an emulated 
    # disk. |numBytes| must be an integral of the block size. If |numBytes| > 0 and a file 
    # named |filename| already exists, then the file may be overridden. Returns -1 on 
    # failure and a disk number on success.
    def mountDisk(self, filename, numBytes):
        #from os.path import isfile

        if numBytes % BLOCK_SIZE():
            return -1

        if numBytes > 0:
            mode = "wb+"
        elif numBytes == 0:
            mode = "ab+"
        else:
            return -2

        try:
            f = open(filename, mode)
            self.openDisks.append(f)
            
            if numBytes > 0:
                self.diskSizes[f] = numBytes / BLOCK_SIZE()
            else:
                f.seek(0,2)
                self.diskSizes[f] = f.tell()

            self.freeBlocks[f] = [0] * self.diskSizes[f]
            self.freeBlocks[f][0] = 1
        except:
            return -3

        return self.openDisks.index(f)

    # Unmounts disk specified by |disk|.
    def unmountDisk(self, disk):
        self.openDisks[disk].close()

    # Reads a block from disk number |disk| at logical position |blockNum| and writes it to
    # |block|. Returns 0 on success and -1 or smaller on disk error. Decryption will also be
    # performed in this function.
    def readBlock(self, disk, blockNum, block):
        if disk > len(self.openDisks) or disk < 0:
            return -2

        if self.openDisks[disk].closed:
            return -4

        if  blockNum > self.diskSizes[self.openDisks[disk]] or blockNum < 0:
            return -5

        self.openDisks[disk].seek(blockNum * BLOCK_SIZE())
        block.setData(self.openDisks[disk].read(BLOCK_SIZE()))
        return 0

    # Writes a block |block| to disk number |disk| at logical position |blockNum|. 
    # Encryption shall be performed in this function. Returns -1 or smaller on error and
    # 0 on success.
    def writeBlock(self, disk, blockNum, block):
        if disk > len(self.openDisks) or disk < 0:
            return -2

        if self.openDisks[disk].closed:
            return -4

        if  blockNum > self.diskSizes[self.openDisks[disk]] or blockNum < 0:
            return -5

        self.openDisks[disk].seek(blockNum * BLOCK_SIZE())
        self.openDisks[disk].write(block.getData())
        self.freeBlocks[self.openDisks[disk]][blockNum] = 1
        return 0

    def freeBlock(self, disk, size):
        if disk > len(self.openDisks) or disk < 0:
            return -2

        if self.openDisks[disk].closed:
            return -4

        for i in range(self.diskSizes[self.openDisks[disk]]):
            freeblocks = 0

            for j in range(size):
                freeblocks = j
                if self.freeBlocks[self.openDisks[disk]][i + j]:
                    break

            if freeblocks == size - 1:
                return i

        return -1
