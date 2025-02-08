#!/usr/bin/env python
'''
./mon.py is a live monitor script. modify monconf.py to fit your needs.
Usage:
  ./mon.py genconf
  ./mon.py data.py def.py
'''
import os, sys
import re
import time
import itertools
import string
import collections
import traceback
import pprint

def debug(msg):
    if os.getenv('debug'): print msg
class Fail(Exception):
    def __init__(self, msg, obj=None):
        self.msg, self.obj = msg, obj
    def __repr__(self):
        return 'Fail: %s %s'%(self.msg, self.obj != None and pprint.pformat(self.obj) or '')
    def __str__(self):
        return repr(self)

def myformat(x):
    if type(x) == float:
        return '%6g'%(x)
    elif type(x) == str:
        return x
    elif isinstance(x, collections.Iterable):
        return ' '.join(myformat(i) for i in x)
    else:
        return str(x)

class DataGen:
    def __init__(self, src, ikey):
        self.src, self.ikey, self.ov, self.nv = src, ikey, {}, {}
        self.code = compile(file(src).read(), src, 'exec')
    def refresh(self, cur_time):
        self.ov = self.nv
        self.nv = locals()
        globals().update(ds=self)
        t = int(cur_time)
        exec self.code in globals(), locals()
    def get(self, key): return eval(key, globals(), self.nv)

class StatRow:
    def __init__(self, ikey, sortkey, cols):
        self.ikey, self.sortkey, self.cols = ikey, sortkey, cols
    def __str__(self): return '\t'.join(map(myformat, [self.ikey] + self.cols))

import cProfile, pstats
class StatMonitor:
    def __init__(self, data_file, init_file):
        def fake_instance_key_gen(): return ['stat']
        def getp(env, k, v): return os.getenv(k, env.get(k, v))
        execfile(init_file, globals(), locals())
        self.report_interval, self.report_list, self.sortkey = int(getp(locals(), 'report_interval', 1)), getp(locals(), 'report_list', '').split(), getp(locals(), 'sortkey', '')
        self.data_file = data_file
        self.instance_key_gen = locals().get('instance_key_gen', None)
        self.data_gen = {}
    def purge(self, ikey_list):
        ikey_set = set(ikey_list)
        for k in self.data_gen.keys():
            if k not in ikey_set:
                del self.data_gen[k]
    def get_data_gen(self, ikey):
        if ikey not in self.data_gen:
            self.data_gen[ikey] = DataGen(self.data_file, ikey)
        return self.data_gen[ikey]
    def header(self): return '%hhh\t' + '\t'.join(k.split('.')[-1] for k in self.report_list)
    def get_stat_row(self, ikey, cur_time):
        dg = self.get_data_gen(ikey)
        try:
            dg.refresh(cur_time)
        except Fail as e:
            return None
        return StatRow(ikey or 'STAT',  dg.get(self.sortkey), [dg.get(k) for k in self.report_list])
    def dump(self):
        cur_time = time.time()
        ikey_list = self.instance_key_gen() if self.instance_key_gen else ['']
        self.purge(ikey_list)
        result = filter(None, [self.get_stat_row(ikey, cur_time) for ikey in ikey_list])
        result.sort(key=lambda x: x.sortkey, reverse=True)
        print '\n'.join(map(str, result[:30]))
        sys.stdout.flush()
    def debug_dump(self):
        cProfile.runctx('self.dump()', globals(), locals(), 'pstat')
        p = pstats.Stats('pstat')
        p.sort_stats('time').print_stats(30)
        sys.exit(1)
    def monitor(self):
        def sleep2(end_time):
            remain_time = end_time - time.time()
            if remain_time > 0: time.sleep(remain_time)
        start_time = time.time()
        for i in itertools.count(1):
            if self.instance_key_gen or (i % 30) == 0: print self.header()
            self.dump()
            sleep2(start_time + i * self.report_interval + 0.01)

# data generate function
class Diff:
    def get_diff(self, k): return ds.nv.get(k, 0) - ds.ov.get(k, 0)
    def __getattr__(self, k): return self.get_diff(k)

class DiffByTime(Diff):
    def __getattr__(self, k):
        t = int(self.get_diff('t'))
        if t == 0: return 0
        else: return self.get_diff(k)/t

d, dt = Diff(), DiffByTime()

class Vector(list):
    def __add__(self, other):
        if isinstance(other, collections.Iterable):
            return Vector(map(lambda x, y: x + y, self, other))
        else:
            return Vector(map(lambda x: x + other, self))
    def __sub__(self, other):
        if isinstance(other, collections.Iterable):
            return Vector(map(lambda x, y: x - y, self, other))
        else:
            return Vector(map(lambda x: x - other, self))
    def __mul__(self, other):
        if isinstance(other, collections.Iterable):
            return Vector(map(lambda x, y: x * y, self, other))
        else:
            return Vector(map(lambda x: x * other, self))
    def __div__(self, other):
        def safe_div(x, y):
            if y == 0:
                return 0
            else:
                return x/y
        if isinstance(other, collections.Iterable):
            return Vector(map(lambda x, y: safe_div(x, y), self, other))
        else:
            return Vector(map(lambda x: safe_div(x, other), self))

def to_list(x):
    if type(x) == str:
        return x.split()
    elif isinstance(x, collections.Iterable):
        return list(x)
    else:
        return [x]
def safe_float(x):
    try:
        return float(x)
    except:
        return x

def unroll(li): return reduce(lambda a, b: a + b, map(list, li), [])

class ParamList(list):
    def __init__(self, keys):
        self.keys = to_list(keys)
        list.__init__(self)
    def build(self, vals_list):
        self.extend(dict(zip(self.keys, to_list(vals))) for vals in to_list(vals_list))
        return self
    def sub(self, args):
        def safe_sub(x, e): return string.Template(x).safe_substitute(**e) if type(x) == str else x
        return [[safe_sub(x, p) for x in args] for p in self]

class DataDef:
    def __init__(self, func, *args):
        self.func, self.args = func, args
    def get(self): return self.data
    def update(self, data):
        self.data = data
        return self
    def apply(self): return self.update(self.func(*self.args))
    def apply_multi(self, param_list):
        return self.update([self.func(*args) for args in param_list.sub(self.args)])
    def tuple(self): return self.update(map(safe_float, to_list(self.data)))
    def matrix(self): return self.update([map(safe_float, to_list(r)) for r in to_list(self.data)])
    def transpose(self): return self.update(zip(*self.data))
    def vector(self): return self.update(map(Vector, self.data))
    def unroll(self): return self.update(unroll(self.data))

def build_regexp(pat):
    special_pat = dict(N='(\d+)', D='(dddd-dd-dd dd:dd:dd.d+)'.replace('d', '\d'), IP='([0-9]+[.][0-9]+[.][0-9]+[.][0-9]+)', CV='{"[A-Z]+":(.*)}', W='(\w+)', S='.*')
    return string.Template(pat).safe_substitute(**special_pat).replace(' ', '\s+')

def fmatch(path, rexp):
    try:
        with open(path, "r") as f:
            content = f.read()
    except IOError:
        raise Fail("open file fail: %s"%(path))
    return re.search(build_regexp(rexp), content).groups()

from subprocess import Popen,PIPE,STDOUT
def popen(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    return p.communicate()[0]

class ConnPool:
    def __init__(self):
        self.pool = {}
    def get(self, conn_str, **kw):
        if conn_str not in self.pool:
            self.pool[conn_str] = SqlConn(conn_str, **kw)
        return self.pool.get(conn_str)

conn_pool = ConnPool()
def sql(expr, conn_str='', **kw):
    global conn_pool
    return conn_pool.get(conn_str or os.getenv('CONN_STR'), **kw).query(expr)

try:
    import MySQLdb as sql_connector
except ImportError:
    import mysql.connector as sql_connector
class SqlConn:
    def __init__(self, conn_str, user='root', passwd='', database='oceanbase'):
        m = re.match('^(.*?):(.*?)$', conn_str)
        if not m: raise Fail('invalid conn str', conn_str)
        ip, port = m.groups()
        self.conn = sql_connector.connect(host=ip, port=int(port), user=user, passwd=passwd, db=database, connect_timeout=1)
    def commit(self):
        return self.conn.commit()
    def query(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        if not result: raise Fail('query empty result: %s'%(sql))
        return unroll(result) if 'unroll result' in sql else result

def get_pid_list(): return [p for p in os.listdir('/proc') if p.isdigit()]
def pname(pid):
    try:
        return os.path.realpath('/proc/%s/exe'%(pid))
    except OSError as e:
        raise Fail("fail to get process name: %s"%(pid))

__init_example__ = '''
def instance_key_gen(): return get_pid_list()
sortkey = 'dt.utime'
if locals().get('instance_key_gen'):
    report_list = 't+00000000 exe status dt.utime dt.stime vm rss dt.rb dt.wb'
else:
    report_list = 't+00000000 dt.cpu dt.ib dt.ob dt.rpc dt.trx'
'''

__data_example__ = '''
pid = self.ikey
if self.ikey:
    pid = self.ikey
    _, exe, status, _, _, _, _, _, _, _, _, _, _, utime, stime = DataDef(fmatch, '/proc/%s/stat'%(pid), '$N \((.+)\) $W $N $N $N $N -?$N $N $N $N $N $N $N $N').apply().tuple().get()
    vm, rss = DataDef(fmatch, '/proc/%s/statm'%(pid), '$N $N').apply().tuple().get()
    exe = exe[-6:]
    rb, wb = DataDef(fmatch, '/proc/%s/io'%(pid), 'read_bytes: $N write_bytes: $N').apply().tuple().get()
else:
    cpu, = DataDef(fmatch, '/proc/stat', 'cpu $N').apply().tuple().get()

    net_dev = ParamList('dev').build('lo bond0')
    ib, ipkt, _, _, _, _, _, _, ob, opkt = DataDef(fmatch, '/proc/net/dev', '$dev:$N $N $N $N $N $N $N $N $N $N').apply_multi(net_dev).matrix().transpose().vector().get()

# disk
# disk_dev = ParamList('dev').build('sda sdb')
# read_count, _, read_sector, read_time, write_count, _, write_sector, write_time = DataDef(fmatch, '/proc/diskstats', '$dev $N $N $N $N $N $N $N $N').apply_multi(disk_dev).matrix().transpose().vector().get()

if os.getenv('CONN_STR'):
    rpc, trx = DataDef(sql, "/*unroll result*/select value from __all_virtual_sysstat where name in ('rpc packet in', 'trans commit count') group by name").apply().tuple().get()
'''

def help(): print __doc__
def genconf():
    file('data.py', 'w').write(__data_example__)
    file('def.py', 'w').write(__init_example__)
    print 'generate data.py,def.py'
def start(data_file, init_file): StatMonitor(data_file, init_file).monitor()
len(sys.argv) >= 2 or help() or sys.exit(1)
func = globals().get(sys.argv[1])
if func:
    func(*sys.argv[2:])
else:
    try:
        start(sys.argv[1], sys.argv[2])
    except Fail as e:
        print e
