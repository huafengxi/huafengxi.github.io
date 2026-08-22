#!/usr/bin/env python2
"""
./bind-cpu.py show_thread_bind <pid>
./bind-cpu.py show_irq_bind eth

# print bind cmd, export ex=1 to actually execute.
./bind-cpu.py bind_thread <pid> tm=tm.py
./bind-cpu.py unbind_thread <pid>
./bind-cpu.py bind_irq eth spec=0..64

# cat tm.py
thread_type_map = [
    ('ThreadName: CLGWR', 'IODISK'),
    ('ThreadName: EasyIO', 'EASY'),
    ('ThreadName: TNT', 'Worker'),
    ]

default_spec = 'EASY:2,Worker:+0..16'
"""
import sys
import re
import itertools
from subprocess import Popen, PIPE
import os
def read(path): return file(path).read()
def popen(cmd): return Popen(cmd, shell=True, stdout=PIPE).communicate()[0]
def execute(cmd):
    ex = int(os.getenv('ex', '0'))
    if ex: print '%s # result %s'%(cmd, popen(cmd))
    else: print cmd 
def calc_bind_spec(rule):
    def make_mask(s, c): return hex(((1<<c) - 1) << s).replace('L', '')
    def move(p, s):
        if s[0] not in '+-': return int(s)
        return p + int(s)
    spec = dict()
    p = 0
    for thread_type,bind_style,id_range in re.findall('(\w+):(?:(\w+):)?([0-9.+-]+)', rule):
        if not bind_style: bind_style = 's'
        if '..' in id_range:
            s, e = id_range.split('..')
        else:
            s, e = '+0', id_range
            if e[0] not in '+-': e = '+' + e
        start = move(p, s)
        end =  move(start, e)
        p = end
        spec[thread_type] = dict(style=bind_style, mask=make_mask(start, end - start), comment='[%d,%d)'%(start, end))
    return spec

def bind_by_rr(d):
    if not 'mask_gen' in d:
        d['mask_gen'] = itertools.cycle(itertools.ifilter(lambda x: x, [int(d['mask'], 16) & (1<<i) for i in range(64)]))
    return hex(d['mask_gen'].next()).replace('L', '')

def bind_by_s(d):
    return d['mask']

def guess_thread_type(bt, rule):
    for pat, type in rule:
        if re.search(pat, bt): return type
    return 'misc'

def parse_thread_bt(ps):
    rexp = '^Thread \d+ \(LWP (\d+)\).*?\n(.*?)(?=\nThread)'
    return dict(re.findall(rexp, ps + '\nThread', re.M|re.S))
def get_thread_trace(pid, ps):
    def get_prname(pid, tid): return file('/proc/%s/task/%s/comm'%(str(pid), str(tid))).read()
    bt = parse_thread_bt(ps and read(ps))
    for tid in os.listdir('/proc/%s/task/'%(pid)):
        try:
            tname = read('/proc/%s/task/%s/comm'%(pid, tid)).strip()
        except IOError as e:
            print '%s not exist'%(tid)
            continue
        yield tid, 'ThreadName: %s\n'%(get_prname(pid, tid)) + bt.get(tid, '')

def post_filt(spec): return spec
def bind_thread(pid, ps='', tm='tm.py', spec='default'):
    execfile(tm, globals(), globals())
    if spec == 'default': spec = default_spec
    spec = post_filt(calc_bind_spec(spec))
    misc = spec.get('misc')
    for tid, bt in get_thread_trace(pid, ps):
        type = guess_thread_type(bt, thread_type_map)
        bind_param = spec.get(type, misc)
        if not bind_param:
            # print '# %s %s'%(tid, type)
            continue
        bind_func = globals().get('bind_by_%s'%(bind_param['style']))
        mask = bind_func(bind_param)
        execute('taskset -p %s %s # %s'%(mask, tid, type))
    print '# host=%s bind_rule=%s'%(popen('hostname -i').strip(), tm)

def get_cpu_count(): return int(popen('grep -c processor /proc/cpuinfo'))
def unbind_thread(pid):
    print 'taskset -a -c -p 0-%d %s'%(get_cpu_count()-1, pid)

def show_thread_bind(pid):
    def format_cpu_mask(x): return '%064s %016s'%(bin(x)[2:], hex(x)[2:])
    def format_thread_count(x): return ' '.join('%s: %d'%(name, count) for name, count in sorted(x.items(), key=lambda x: x[0]))
    stat = {}
    for tid in os.listdir('/proc/%s/task/'%(pid)):
        cpuset = popen("taskset -p %s | awk '{print $NF}'"%(tid)).strip()
        tname = read('/proc/%s/task/%s/comm'%(pid, tid)).strip()
        print '%s %s %s'%(tid, tname, cpuset)
        tname = re.sub('\d+', 'X', tname)
        if cpuset not in stat:
            stat[cpuset] = dict()
        if tname not in stat[cpuset]:
            stat[cpuset][tname] = 0
        stat[cpuset][tname] += 1
    stat = sorted(stat.items(), key=lambda x: int(x[0],16))
    print '####### thread bind stat ######'
    print '\n'.join('%s: %s'%(format_cpu_mask(int(k, 16)), format_thread_count(v)) for k,v in stat)

def get_irq_map(): return dict(re.findall('^ *(\d+):[0-9 ]+(.+)', read('/proc/interrupts'), re.M))
def get_irq_list(pat): return [no[0] for no in re.findall('^ *(\d+):.*(%s).*'%(pat), read('/proc/interrupts'), re.M)]
def bind(irq, cpu_id):
    return 'echo %s >/proc/irq/%s/smp_affinity_list'%(cpu_id, irq)
    def make_mask(id):
        hex = ('%016x'%(1<<id))
        return id < 32 and '%08x'%(1<<id) or id < 64 and '%s,%s'%(hex[:8], hex[8:])
    return 'echo %s >/proc/irq/%s/smp_affinity_list'%(make_mask(int(cpu_id)), irq)

def make_cpu_list(spec):
    s, e = spec.split('..')
    return range(int(s), int(e))
def bind_irq(pat, cpu_list):
    cpu_list = make_cpu_list(cpu_list)
    cpu_id_list = itertools.cycle(cpu_list)
    for irq in get_irq_list(pat):
        execute(bind(irq, cpu_id_list.next()))

def show_irq_bind(pat):
    def first_int(x): return int(x.split('-')[0])
    mask_count = {}
    irq_name = get_irq_map()
    for irq in get_irq_list(pat):
        mask = read('/proc/irq/%s/smp_affinity_list'%(irq)).strip()
        print '%s %s %s'%(irq, mask, irq_name[irq])
        if mask in mask_count:
            mask_count[mask] += 1
        else:
            mask_count[mask] = 1
    mask_count = sorted(mask_count.items(), key=lambda x: first_int(x[0]))
    print ' '.join('%s/%s'%(k,v) for k,v in mask_count)

def parse_cmd_args(args):  return [i for i in args if not re.match('^\w+=', i)], dict(i.split('=', 1) for i in args if re.match('^\w+=', i))
def help(): print __doc__
if __name__ == '__main__':
    len(sys.argv) > 2 or help() or sys.exit(1)
    func = globals().get(sys.argv.pop(1))
    callable(func) or help() or sys.exit(2)
    args, kw = parse_cmd_args(sys.argv[1:])
    func(*args, **kw)
