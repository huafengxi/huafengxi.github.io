#!/usr/bin/env python3
'''
# file system utility
ls * |fsu.py pmv from to # batch rename, similar to re.sub
fsu.py dfuzz *      # fuzz file content and name ext
fsu.py nfuzz *      # fuzz file base name
fsu.py ls *   # ls fuzz file names
'''
import sys
import os
import re

def pmv(src, dest):
    for f in sys.stdin.readlines():
        f = f.rstrip()
        if re.search(src, f):
            target = re.sub(src, dest, f)
            print("mv '%s' '%s'"%(f, target))
char_map = 'iFXhbcNYDuUgsjrIMJwTpPAqnyvOfSxeEzWBkdtQmlZCoRVKLGHa'
def fuzz_str(f):
    def translate_char(x):
        i = char_map.find(x)
        return char_map[i^1] if i >= 0 else x
    return ''.join(map(translate_char, f))
def ls(*flist):
    for f in flist:
        print("%s %s"%(f, fuzz_str(f)))

import itertools
def xor_data_block(data):
    fuzz_str = itertools.cycle(char_map)
    return [i ^ ord(next(fuzz_str)) for i in data]
def fuzz_one_file(path):
    with open(path, 'rb+') as f:
        data = f.read(1<<21)
        f.seek(0)
        data = xor_data_block(data)
        f.write(bytes(data))
def fuzz(*flist):
    for f in flist:
        fuzz_one_file(f)
        os.rename(f, fuzz_str(f))
def dfuzz(*flist):
    for f in flist:
        fuzz_one_file(f)
        base, ext = os.path.splitext(f)
        os.rename(f, base + fuzz_str(ext))
def nfuzz(*flist):
    for f in flist:
        base, ext = os.path.splitext(f)
        os.rename(f, fuzz_str(base) + ext)

def help(): print(__doc__)
len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None:
    print(ret)
