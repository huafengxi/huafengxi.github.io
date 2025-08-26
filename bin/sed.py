#!/usr/bin/env python
'''
./sed.py diff 'expr' file1... # generate a patch
# expr could be a callable function, or a (from, to) tuple
# with function, file content will be set to func(content)
# with (from,to) tuple, file content will be set to re.sub(from, to, content)
'''
import re
import sys
import os, subprocess

def popen(cmd, content):
    return subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(content)[0]

def diff(expr, *filelist):
    for f in filelist:
        d = open(f).read()
        n = eval(expr)
        if callable(n):
            n = n(d)
        if type(n) == tuple:
            n = re.sub(n[0], n[1], d)
        p = gen_file_patch(f, n)
        if p: print p

def gen_file_patch(f, new_content):
    def jp(d, p): return os.path.join(d, p)
    header = '--- %s\n+++ %s\n'%(jp('a', f), jp('b', f))
    result = popen('diff -u %s -|tail -n +3'%(f,), new_content)
    return result and header + result or None

def ccpatch(content):
    frm = '(?m)^export CC=(.+)\nexport CXX=(.+)\n'
    to = '''
export FDO_CFLAGS='-fno-reorder-blocks-and-partition -Wl,--emit-relocs'
export CC="\\1 $FDO_CFLAGS"
export CXX="\\2 $FDO_CFLAGS"
'''
    return re.sub(frm, to, content)

def help(): print __doc__
len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None: print ret

