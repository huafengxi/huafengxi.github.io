#!/bin/env python2
'''
./encoding.py correct_path dir
./encoding.py to_utf8 a.txt
'''
import os
import chardet

def sh(cmd): return os.system(cmd)
def read(path):
    with open(path) as f:
        return f.read()

def write(path, text):
    with open(path, 'wb') as f:
        f.write(text)

def to_utf8(path):
    text = read(path)
    if not text: return
    encoding = chardet.detect(text)['encoding']
    if encoding.lower() in ('shift_jis', 'cp932', 'gbk', 'gb2312'):
        sh("mv '%s' '%s.bak'"%(path, path))
        write(path, text.decode(encoding).encode('utf-8'))
    if encoding not in ('UTF-8-SIG', 'utf-8', 'ascii', None):
        print '%s: %s'%(path, encoding)

def detect(text):
    def safe_decode(text, code):
        try:
            return text.decode(code, 'ignore').encode('utf-8')
        except Exception as e:
            print e
            return 'fail'
    print 'raw: %s'%(text)
    for code in all_encodings:
        print '%s: %s'%(code, safe_decode(text, code))

def get_orig_path(text):
    return text.decode('shift_jis', 'ignore').encode('utf-8')

def do_correct_path(arg, dir, files):
    new_files = []
    for f in files:
        orig_path = get_orig_path(f)
        if f == orig_path:
            continue
        new_files.append(orig_path)
        sh("mv '%s/%s' '%s/%s'"%(dir, f, dir, orig_path))
    del files[:]
    files.extend(new_files)
def correct_path(dir):
    os.path.walk(dir, do_correct_path, None)

import sys
def help(): print __doc__
len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None:
    print ret

