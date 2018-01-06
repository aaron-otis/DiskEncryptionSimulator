# Functions to convert strings

# hexify takes an ASCII string and returns a hexadecimal string
def hexify(astr):
    from binascii import b2a_hex

    return b2a_hex(astr)

# unhexify takes a hexadecimal string and returns an ASCII string
def unhexify(hstr):
    from binascii import a2b_hex

    return a2b_hex(hstr)


# b64_hex takes a base 64 encoded string and returns the hexadecimal equivalent
def b64_hex(b64str):
    from binascii import a2b_base64, b2a_hex

    return b2a_hex(a2b_base64(b64str))

# hex_b64 takes a hexadecimal string and returns the base 64 encode equivalent
def hex_b64(hstr):
    from binascii import b2a_base64, a2b_hex

    return b2a_base64(a2b_hex(hstr))

# b64ify takes an ASCII string and returns it encoded in base 64
def b64ify(astr):

    return hex_b64(hexify(astr))

# unb64ify takes a base 64 encoded string and returns the decoded ASCII string
def unb64ify(b64str):

    return unhexify(b64_hex(b64str))
