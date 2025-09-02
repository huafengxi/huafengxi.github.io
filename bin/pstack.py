#!/usr/bin/env python2
"""
pstack <pid> | pstack.py  # equal to: pstack <pid> | pstack.py group
pstack <pid> | match=negative pstack.py filt <pattern>         # filt stack by regexp <pattern>
pstack <pid> | pstack.py group                  # group same stack
pstack <pid> | pstack.py addr2line -sfC -p <pid>|-e observer.debug # replace <hex-addr> to symbole  # useful when pstack is generated without debug info.
pstack <pid> | pstack.py tid2name <tid2name.map>|<pid>  # ps -T -o tid,comm <pid> > tid_name.map
pstack <pid> | pstack.py flat                   # print stack in the line as: thread-no frame-no stack-addr ...  # maybe useful for gdb script
"""

import sys
import re
import os
import itertools
from subprocess import Popen, PIPE
import pprint

def help():
    print(__doc__)

def pstack(stack_trace):
    rexp = '^Thread.*?LWP ([^)]+).*?\n(.*?)(?=\nThread)'
    return re.findall(rexp, stack_trace + '\nThread', re.M|re.S)

def normal_top_frame_addr(text):
    return re.sub('#0  (0x[0-9a-f]+) ', '#0  0x0000000000000000 ', text)

def get_stack_trace_key(text):
    def get_line_key(line):
        m = re.match('(.*?)[<(]', line)
        return m and m.group(1) or ''
    return [get_line_key(line) for line in text.split('\n')]

def group(text):
    # text = normal_top_fram_addr(text)
    stack_list = pstack(text)
    key_func = lambda x: get_stack_trace_key(x[1])
    grp_list = [list(grp) for key, grp in itertools.groupby(sorted(stack_list, key = key_func), key_func)]
    for grp in sorted(grp_list, key=lambda x: len(x), reverse=True):
        yield 'TID: %s'%(' '.join(tid for tid,stack in grp))
        yield grp[0][1]

def flat(text):
    for tid, bt in pstack(text):
        for frame_no, frame_desc in re.findall('#(\d+) (.*)$', bt, re.M):
            yield '%s\t%s\t%s'%(tid, frame_no, frame_desc)

def filt(text, pat, limit=30):
    for tid, bt in pstack(text):
        m = re.search(pat, tid + bt)
        if (m if os.getenv('match') != 'negative' else not m):
            yield 'Thread (LWP %s)\n%s\n'%(tid, bt)

def obstack(text):
    os.environ['match'] = 'negative'
    return group(''.join(filt(text, 'nanosleep|pthread_cond_wait|pthread_cond_timedwait|epoll_wait|epoll_pwait|__io_getevents|ObLightyQueue|ObPriorityQueue|ObClockGenerator|ObPurgeWorker|easy_baseth_pool_monitor_func')))

def addr2line(text, *cmd):
    # addr_list = set(re.findall('0x[0-9a-z]{16}', text))
    addr_list = set(re.findall('0x[0-9a-z]{7,}', text))
    sym_output = Popen(['/usr/bin/xargs', 'eu-addr2line'] + list(cmd), shell=False, stdin=PIPE, stdout=PIPE).communicate('\n'.join(addr_list))[0]
    sym_list = [sym.replace('\n', ' ') for sym in re.findall('^[^\n]+\n[^\n]+\n', sym_output, re.M)]
    sym_tab = dict(zip(addr_list, sym_list))
    def get_sym(addr):
        sym = sym_tab.get(addr, 'unkonwn')
        return addr + ' ' + sym
    yield re.sub('0x[0-9a-z]+', lambda m: get_sym(m.group(0)) + '\n', text)

def get_tid_name(pid, tid):
    return safe_read('/proc/{}/task/{}/comm'.format(pid, tid)).strip()

def tid2name(text, pid):
   map_text = file(pid).read() if os.path.exists(pid) else Popen('ps -T -o tid,comm {}'.format(pid), shell=True, stdout=PIPE).communicate()[0]
   tid_name = dict(re.findall('(\d+)\s+(\w+)', map_text))
   yield re.sub('LWP (\d+)', lambda m: 'LWP {}_{}'.format(m.group(1), tid_name.get(m.group(1), 'unknown')), text)

def to_str(iter): return '\n'.join(iter)

if __name__ == '__main__':
    (len(sys.argv) >= 2 or not sys.stdin.isatty()) or help() or sys.exit(1)
    if len(sys.argv) < 2:
        sys.argv.insert(1, 'group')
    action = globals().get(sys.argv[1], None)
    if not callable(action):
        help()
        sys.exit(2)
    else:
        print to_str(action(sys.stdin.read(), *sys.argv[2:]))
