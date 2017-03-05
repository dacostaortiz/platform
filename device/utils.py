import shutil
import os
from os.path import isfile, join
import hashlib
 
def checksum(f):
    hasher = hashlib.md5()
    with open(f, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return(hasher.hexdigest())

def exist_file(path):
    return any(isfile(join(path, i)) for i in os.listdir(path))

def mv_file(src,dest):
    shutil.move(src, dest)
