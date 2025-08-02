cpdef str_to_bytearray(str text):
    return bytearray([ord(c) & 0xff for c in text])
