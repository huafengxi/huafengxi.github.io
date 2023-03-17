#!/usr/bin/env python2
'''
cat a.txt | ./diff.py num_diff base.txt
'''
import sys
import re

def read(path):
    return file(path).read()

def num_diff(bfile):
    def diff_text(t, b):
        t, b = int(t), int(b)
        return '%d %d'%(t, t - b)
    text1, base = sys.stdin.read(), read(bfile)
    base_list = re.findall('\d+', base)
    biter = iter(base_list)
    return re.sub('\d+', lambda m: diff_text(m.group(0), biter.next()), text1)

def help(): print __doc__
len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None:
    print ret
