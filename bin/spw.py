#!/usr/bin/env python2
'''
dryrun=1 ./spw.py spec
# spec file example
2x1
watch date # time
watch df -h # diskutil
'''
import sys
import os
import re
import subprocess

def term_size(): return map(int, subprocess.Popen(['stty', 'size'], stdout=subprocess.PIPE).communicate()[0].strip().split())
def calc_wsize(m, n):
    x, y = term_size()
    return y/m, x/n
def split_win(m, n):
    cmds = []
    w, h = calc_wsize(m, n)
    print 'm=%s n=%s w=%s h=%s'%(m, n, w, h)
    for i in range(n-1):
        cmds.extend([['split-window', '-t', str(i), '-v'], ['resize-pane', '-t', str(i), '-y', str(h)]])
    for i in range(m * n):
        if i % m < m - 1: cmds.extend([['split-window', '-t', str(i), '-h'], ['resize-pane', '-t', str(i), '-x', str(w)]])
    cmds.append(['set', 'pane-border-status', 'top'])
    return cmds
def send_cmds(l): return [['send-keys', '-t',  str(idx), cmd, 'enter'] for idx,cmd in enumerate(l)]

def get_title(c): return c.rsplit('#', 1)[-1].strip()[:16]
def set_title(s): return r'printf "\033]2;%s\033\\"'%(s)
def add_title(c): 
    return set_title(get_title(c)) + ';' + c
def run_tiled(cmd_list, m, n):
    tmux_cmds = list(split_win(m, n)) + send_cmds(add_title(c) for c in cmd_list)
    tmux_cmds = reduce(lambda x,y: x + y, [c + [';'] for c in tmux_cmds], [])
    if os.getenv('dryrun') == '1': print tmux_cmds
    else: subprocess.call(['tmux'] + tmux_cmds)

def help(): print __doc__
sys.stdin.isatty() and len(sys.argv) == 2 or help() or sys.exit(1)
spec = sys.argv[1]
with open(spec) as f:
    cmds = f.readlines()
try:
   m, n = re.match('(\d+)x(\d+)', cmds[0]).groups()
except:
   raise Exception('first line of spec shoud be mxn')
run_tiled([c for c in cmds[1:] if not c.startswith('#') and c.strip()], int(m), int(n))
