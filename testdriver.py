from driver import Block, diskSim, BLOCK_SIZE
from struct import pack
from strings import hexify

diskname = "testdisk"
sim = diskSim()

print("Mounting disk {}".format(diskname))
disk = sim.mountDisk(diskname, 10 * BLOCK_SIZE())
print(disk)

print("Writing to disk")
for i in range(5):
    p = pack(">Q", i)
    sim.writeBlock(disk, i, Block(p * 512))

print("Reading from disk")
for i in range(5):
    b = Block()
    sim.readBlock(disk, i, b)
    s = hexify(b.getData())
    #print(s)
    print(len(s) / 2)

print("Unmounting disk")
sim.unmountDisk(disk)

print("Mounting disk {} with no size specified".format(diskname))
disk = sim.mountDisk(diskname, 0)

print("Reading from disk")
for i in range(5):
    b = Block()
    sim.readBlock(disk, i, b)
    s = hexify(b.getData())
    #print(s)
    print(len(s) / 2)
