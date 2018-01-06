# Implementation of XOR 

def xor(m, k):
    i, j = 0, 0
    ret = ""

    while i < len(m):
        ret += chr(ord(m[i]) ^ ord(k[j]))
        i += 1
        j += 1

        if j >= len(k):
            j = 0

    return ret
