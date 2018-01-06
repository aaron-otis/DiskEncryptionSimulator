from os import urandom
from diskencrypt import diskEncrypt
from driver import BLOCK_SIZE

filename = "testdisk"
enc = diskEncrypt()

res = enc.createDisk(filename, 10 * BLOCK_SIZE(), "password")
print(res)

enc.closeDisk(filename)
res = enc.openDisk(filename, "password")
print(res)

res = enc.write(urandom(4096), 4096, 8000)
print(res)
