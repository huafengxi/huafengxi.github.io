#!/bin/env python2
'''
purge-file.py orphan # same as below cmd
find . -name '*.h' -or -name '*.c' -or -name '*.cpp' -or -name 'CMakeLists.txt' | purge-file.py orphan CMakeLists.txt # print file unrefed by any CMakeLists.text
purge-file.py empty  # same as below cmd
find . -type d | purge-file.py empty '*.cpp' # print dir contain nothing other than '*.cpp'
'''
import sys, os, re
import subprocess
import cPickle
class Proc:
    def __init__(self, func, *args, **kw):
        self.result = None
        rfd, wfd = os.pipe()
        self.pid = os.fork()
        if self.pid > 0:
            os.close(wfd)
            self.rfd = rfd
        else:
            os.close(rfd)
            ret = func(*args, **kw)
            os.write(wfd, cPickle.dumps(ret))
            sys.exit(0)
    def get(self, timeout=None):
        ret = os.read(self.rfd, 1<<26)
        os.close(self.rfd)
        os.waitpid(self.pid, 0)
        return cPickle.loads(ret)

def ListHandle(f):
    def handle_list(li): return [f(i) for i in li]
    return handle_list
class ParMap:
    def __init__(self, func, li, nproc=32):
        batch = (len(li) + nproc)/nproc
        self.result = [Proc(func, li[s:s+batch]) for s in range(0, len(li), batch)]
    def get(self, timeout=None):
        result = []
        for r in self.result:
            result.extend(r.get(timeout))
        return result

def is_text(p):
    h = file(p).read(100)
    try:
        h.decode('ascii')
        return True
    except:
        return False

def read_include(p):
    return '\n'.join(re.findall('^#include', file(p).read(), re.M))

def read2(p):
    if re.match('[.](h|c|cpp|cxx|ipp)$', p):
        return read_include(p)
    if os.path.isfile(p):
       return file(p).read() if is_text(p) else ''
    return '\n'.join(os.listdir(p))

def get_input(fallback_cmd):
    if sys.stdin.isatty():
        return subprocess.Popen(fallback_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
    return sys.stdin.read()

def get_flist(cmd):
    return filter(None, get_input(cmd).split('\n'))

def calc_orphan_set(root_set, orphan_set):
    basename_set = set(os.path.basename(i) for i in orphan_set)
    def read_fname(li):
        return list(set(re.findall('[_a-zA-Z0-9.]+', '\n'.join(read2(i) for i in li))) & basename_set)
    root_context = '\n'.join(ParMap(read_fname, root_set).get())
    def is_reachable(i): return os.path.basename(i) in root_context
    reachable_set = ParMap(ListHandle(is_reachable), orphan_set).get()
    new_root_set, new_orphan_set = [], []
    for idx, i in enumerate(orphan_set):
        if reachable_set[idx]:
            new_root_set.append(i)
        else:
            new_orphan_set.append(i)
    return new_root_set, new_orphan_set

def orphan(pat='CMakeLists.txt'):
    flist = get_flist("find . -name '*.h' -or -name '*.c' -or -name '*.cpp' -or -name 'CMakeLists.txt'")
    new_reachable = [i for i in flist if re.search(pat, i)]
    orphan_set = list(set(flist) - set(new_reachable))
    while new_reachable:
        new_reachable, orphan_set = calc_orphan_set(new_reachable, orphan_set)
    return '\n'.join(sorted(orphan_set))

def empty(pat=r'\w+'):
    dlist = get_flist("find . -type d")
    return '\n'.join(p for p in dlist if not re.search(pat, '\n'.join(os.listdir(p))))

def help(): print __doc__

len(sys.argv) > 1 or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
print func(*sys.argv[2:])
