import hashlib
 
def checksum(f):
    hasher = hashlib.md5()
    with open(f, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return(hasher.hexdigest())
