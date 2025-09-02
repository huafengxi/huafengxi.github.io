#!/usr/bin/python2
# -*- coding: utf-8 -*-
'''
https://huafengxi.github.io/2021/05/26/git-list-missing-patch.html
cat a2b.log | git.py extract_desciption |git.py filt b2a.log
'''
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import os
import re

def wash_description(text):
    def remove_square(x): return re.sub('\[[^\]]+\]', '', x)
    def squash_space(x): return re.sub('\s+', ' ', x)
    return squash_space(remove_square(text)).strip()

def split_commit(text):
    for c in re.split('^commit ', text, flags=re.M):
        if c: yield 'commit ' + c

def extract_by_re(pat, text):
    m = re.search(pat, text, re.M|re.S)
    if not m: return
    g = m.groups()
    return g[0] if g else m.group(0)

def extract_by_pat_list(pat_list, text):
    for pat in pat_list:
        p = extract_by_re(pat, text)
        if p != None: return p
    return 'extract commit description fail!'

desc_pat_list = ('^ +Task   : (.+?)( +\w+<\w+)?\n', '^ +([^\n]+)\n *\n +Merge')
def extract_description():
    for commit in split_commit(sys.stdin.read()):
        print '### description:', wash_description(extract_by_pat_list(desc_pat_list, commit))
        print commit
def filt(patched_list_file):
    patches = wash_description(file(patched_list_file).read())
    for c in re.split('^### description:', sys.stdin.read(), flags=re.M):
        if not c: continue
        head = c.split('\n', 1)[0].strip()
        if head not in patches: print '### description: '+ c

def show(commit):
    css = '''<style type="text/css">
pre{margin-top:0; margin-bottom:0; color: black; }
.ci_msg { font-weight: bold;}
.add { color: green ;}
.del { color: red; }
 </style>'''
    output = 'git cherry-pick %s\n'%(commit) + Popen('git show %s'%(commit), shell=True, stdout=PIPE).communicate()[0]
    output = re.sub('(?m)^([+].*?)$', r'<span class="add">\1</span>', output)
    output = re.sub('(?m)^([-].*?)$', r'<span class="del">\1</span>', output)
    output = re.sub('(?ms)^(diff --git.*)$', r'<div class="diff"><pre>\1<pre></div>', output)
    output = re.sub('(?s)^(.*)<div', r'<div class="ci_msg"><pre>\1</pre></div>\n<div', output)
    return css + output

def help(): print __doc__

len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help('%s is not callable' % (sys.argv[1])) or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None: print ret
