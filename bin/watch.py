#!/usr/bin/env python2
'''
while true; do echo '%hhh'; date; date; sleep 1; done | page_head='%hhh' watch.py
'''
import sys
def help(): print __doc__
(not sys.stdin.isatty()) or help() or sys.exit(1)

import atexit
import curses
stdscr = curses.initscr()
curses.noecho()
curses.curs_set(0)

def restore_term():
    curses.curs_set(1)
    curses.endwin()
atexit.register(restore_term)
page_head = os.getenv('page_head', '%hhh')
while True:
    line = sys.stdin.readline()
    if line.startswith(page_head):
        stdscr.clear()
        y = 0
    stdscr.addstr(y, 0, line)
    y += 1
    stdscr.refresh()

