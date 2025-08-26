#!/bin/env python2
'''
find deps src -name '*.h' | ./find-const.py
'''

import sys
import re
import os

def help(): print __doc__
not sys.stdin.isatty() or help() or sys.exit(1)

def is_danger(line):
    if '_ID' in line or '_LEN' in line or '_INVALID' in line or 'DEFAULT_' in line : return False
    return True
def parse_const_def(line):
    k, v = line.split('=')[:2]
    k, v = k.strip(), v.strip()
    v, comment = (v + ';').split(';', 1)
    return k.split()[-1], v, comment.strip()
for f in sys.stdin.readlines():
    for line in file(f.strip()).readlines():
        line = line.rstrip()
        pat = '^(static const int)|^(const int)'
        if re.match(pat, line) and is_danger(line):
            k, v, comment = parse_const_def(line)
            print '%s\t%s\t%s\t%s'%(os.path.basename(f.strip()), k, v, comment)
