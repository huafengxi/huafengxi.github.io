#!/usr/bin/env python
'''
* extract and format
cat ... | mline=1 sep=',' grep.py find <pat> # special pattern: $W $N $D $IP $CV $S
cat ... | grep.py find <pat1> <pat2> ... # tree match
grep.py pgrep <pat> files # if <pat> has invisible char, print hit only
echo -e '127.0.0.1\t80' | header='ip port' grep.py format  ssh '$ip $port'
grep xxx | grep.py indent_collapse

* stat
cat ... | stat_interval=1 count_filter=0 avg_filter=0 ./grep.py stat <pat> # special pattern $N
cat ... | ./grep.py top <pat> # pat should include '()'
tail -f ... | ./grep.py tail_stat

* filt
cat ... | ./grep.py is_printable
cat ... | ./grep.py log_reduce
ls log/* |sort | ./grep.py range_filter '2017([0-9]+)' 002000 003000
cat ... | ./grep.py tidy_cpp_filt # remove long c++ template signature.

* tracelog
./grep.py trace <pat> log/observer.log*
grep ... | ./grep.py split_trace
cat ... | ./grep.py filter_tenant # normalize tenant_name, and keep one only

* group
cat a.txt | grep.py group # group by key(first column is key)
cat a.txt | gsize=2 grep.py group # group by size

'''

import sys
import re
import os
import time
import subprocess
import string
from itertools import groupby

def cfgi(key, default):
    return int(os.getenv(key, default))

def tolist(x):
    if type(x) == list or type(x) == tuple:
        return x
    else:
        return [x]

def sh(cmd):
    Popen(cmd, shell=True)

def read(path):
    return file(path).read()

def help():
    print(__doc__)

def parse_ts(str):
    return time.mktime(time.strptime(str, '%Y-%m-%d %H:%M:%S'))

def safe_div(x, y):
    if y == 0:
        return -1.0
    else:
        return x/y

def find_tree(*pats):
    def build_list(matchs):
        r = []
        for x in matchs:
            if type(x) == list or type(x) == tuple:
                r.extend(x)
            else:
                r.append(x)
        return r
    matchs = [''] * len(pats)
    for line in sys.stdin:
        for idx, pat in enumerate(pats):
            m = re.search(pat, line)
            if not m: continue
            matchs[idx] = m.groups()
            if idx == len(pats) - 1:
               result = build_list(matchs)
               if all(result):
                   print('\t'.join(result))

def find(*pats):
    sep = os.getenv('sep', '\t')
    pats = map(build_regexp, pats)
    if len(pats) > 1:
        find_tree(*pats)
        return
    pat = pats[0]
    if cfgi('mline', '0'):
        for i in re.findall(pat, sys.stdin.read(), re.M|re.S):
            print(sep.join(tolist(i)))
    else:
        for line in sys.stdin:
            m = re.search(pat, line)
            if m:
                print(sep.join(m.groups()))

def indent_collapse():
    indent, cur_lines = 65536, []
    def count_leading_space(a): return len(a) - len(a.lstrip())
    for line in sys.stdin:
        i = count_leading_space(line)
        if i > indent:
            cur_lines.append(line.strip())
        else:
            if cur_lines: print(' '.join(cur_lines))
            if i == 0:
                indent, cur_lines = 65536, []
                print(line)
            else:
                indent, cur_lines = i, [line.rstrip()]

    if cur_lines:
        print(' '.join(cur_lines))

import mmap
def fsearch(pat, path):
    return re.search(pat, mmap.mmap(open(path).fileno(), 0))

def pfind(pats, *files):
    pass

def format(*args):
    tpl = re.sub(r'\$([0-9])', r'$k\1', ' '.join(args))
    tpl = string.Template(re.sub(r'\$([0-9])', r'$k\1', ' '.join(args)))
    for line in sys.stdin.readlines():
        values = line.strip().split('\t')
        keys = (os.getenv('header') or '').split() or ['k%d'%(i + 1) for i in range(len(values))]
        print(tpl.safe_substitute(all=line.strip(), **dict(zip(keys, values))))

def build_regexp(pat):
    special_pat = dict(N=r'(\d+)', D='(dddd-dd-dd dd:dd:dd.d+)'.replace('d', r'\d'), IP='([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)', CV='{"[A-Z]+":(.*)}', W=r'(\w+)', S='.*')
    def get_special_pat(x): return special_pat.get(x, '$' + x)
    return re.sub(r'\$([A-Z]+)', lambda m: get_special_pat(m.group(1)), pat)
def stat(pat=''):
    pat = build_regexp(pat)
    stat_interval, count_filter, avg_filter = cfgi('stat_interval', '1'), cfgi('count_filter', '0'), cfgi('avg_filter', '0')
    last_report, last_count, last_accu = 0.0, 0, 0.0
    cur_count, cur_accu = 0, 0.0
    for match in re.findall(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*?%s'%(pat), sys.stdin.read()):
        if type(match) == tuple:
            ts, val = match[0], match[1]
        else:
            ts, val = match, 0
        cur_ts = parse_ts(ts)
        cur_accu += int(val)
        cur_count += 1
        if cur_ts - last_report > stat_interval - 0.1:
            count = cur_count - last_count
            avg = safe_div(cur_accu - last_accu, count)
            if count > count_filter and avg >= avg_filter:
                print('%s\t%d\t%f'%(ts, count, avg))
                last_report, last_count, last_accu = cur_ts, cur_count, cur_accu
  
def top(pat):
    pat = build_regexp(pat)
    time_key_list = re.findall(r'2017-(\d\d-\d\d \d\d:\d\d:\d\d).*%s'%(pat), sys.stdin.read())
    for time, key in sorted(time_key_list, key = lambda x: int(x[1]), reverse=True):
        print('%s %s'%(time, key))

def is_printable():
    return set(sys.stdin.read()).issubset(set(string.printable))

def trace(pat, *file_list):
    file_list = sorted([(f, os.stat(f).st_mtime) for f in file_list], key=lambda x: x[1], reverse=True)
    hit_idx, trace_id = 0, ''
    for idx, (f, mtime) in enumerate(file_list):
        m = re.findall(r'\[(Y[A-Z0-9]+-[A-Z0-9]+)\].*(%s)'%(pat), read(f))
        if m:
            hit_idx = idx
            trace_id = m[-1][0]
            break
    if not trace_id:
        return 'not found trace'
    print('trace_id: %s'%(trace_id))
    subprocess.call('grep %s %s'%(trace_id, ' '.join(f for f, mtime in file_list[hit_idx:hit_idx+1])), shell=True)

def log_group(file, pat, time_limit, frequency_limit, truncate_limit):
    def parse_line(line, pat):
        m = re.search(pat, line, re.M)
        if not m: return 0, ''
        time, key = m.groups()
        ts = parse_ts(time)
        return ts, key
    def print_line(line, count):
        if count > frequency_limit:
            return
        if frequency_limit > 1:
            print('%4d %s'%(count, line.strip()[:truncate_limit]))
        else:
            print(line.strip()[:truncate_limit])
    log_stat = {}
    for line in file:
        ts, key = parse_line(line, pat)
        if not key: continue
        last_ts, count = log_stat.get(key, (0, 0))
        if ts - last_ts > time_limit:
            print_line(line, count)
            log_stat[key] = (ts, 1)
        else:
            log_stat[key] = (last_ts, count + 1)
    
def log_reduce():
    def get_pattern(pat):
        oblog = r'\[(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)\.\d+\] [A-Z]+\s+(?:\[[.A-Z]+\] )?(\S+) .+$'
        return dict(oblog=oblog).get(pat, pat)
    pattern = get_pattern('oblog')
    log_group(sys.stdin, pattern, cfgi('time_window', '60'), cfgi('frequency_limit', '10000'), cfgi('line_truncate_limit', '400'))

def split_trace():
    '''EU: grep Y000111 log/observer.log | ./conv.py split_trace'''
    return sys.stdin.read().replace('|', '\n')

def range_filter(regexp, start, end):
    for line in sys.stdin.readlines():
        line = line.strip()
        m = re.match(regexp, line)
        if not m:
            continue
        if not m.groups():
            key = m.group(0)
        else:
            key = m.group(1)
        if key > start and (not key > end):
            print(line)

def remove_bracket(text):
    text = re.sub('<[^<>]*>', '', text)
    text = re.sub(r'\([^()]*\)', '', text)
    text = re.sub(r'oceanbase::\w+::', '', text)
    return text

def tidy_cpp_sign(text):
    old_text, text = '', text
    while old_text != text:
        old_text = text
        text = remove_bracket(text)
    return text

def tidy_cpp_filt():
    for line in sys.stdin:
        print(tidy_cpp_sign(line), end='')

def filter_tenant():
    tenant_map = {}
    for line in sys.stdin:
        m = re.match(r'(\w+)', line)
        tenant_name = m.group(1)
        tenant_key = re.sub('[0-9]', 'x', tenant_name)
        if tenant_key not in tenant_map:
            tenant_map[tenant_key] = tenant_name
        if tenant_name == tenant_map[tenant_key]:
            print(line)

from itertools import groupby

def group():
    def group_by_id():
        for key, grp in groupby(re.findall('(.*?)\t(.*?)$', sys.stdin.read(), re.M), lambda x: x[0]):
            print('\t'.join([key] + [item[1] for item in grp]))
    def group_by_count(group_size):
        g = []
        for line in sys.stdin:
            g.append(line.strip())
            if len(g) >= group_size:
                print('\t'.join(g))
                g = []
        if g:
            print('\t'.join(g))
    gsize = int(os.getenv('gsize', '0'))
    if gsize > 0:
        group_by_count(gsize)
    else:
        group_by_id()

if __name__ == '__main__':
    len(sys.argv) >= 2  or help() or sys.exit(1)
    func = globals().get(sys.argv[1])
    callable(func) or help() or sys.exit(2)
    ret = func(*sys.argv[2:])
    if ret != None:
        print(ret)
