#!/usr/bin/env python
'''
Usages:
 ./conv.py help
'''
import sys
import os
import time
import traceback
import inspect
import socket
import struct
import random
import re
import binascii
import itertools

def line_iter(f):
    while True:
       line = f.readline()
       if not line: break
       yield line.rstrip()

class UF(list):
    def __init__(self):
        list.__init__(self)
    def __call__(self, func):
        self.append(func)
        return func
    def get(self, name):
        for f in self:
            if f.__name__ == name:
                return f
    def call(self, func_name, args):
        def get_args(func):
            sig = inspect.signature(func)
            return [param.name for param in sig.parameters.values() if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        def get_input(args):
            if args:
                for str in args:
                    yield [str]
            elif not sys.stdin.isatty():
                for line in line_iter(sys.stdin):
                    yield [line]
        func = self.get(func_name)
        callable(func) or self.help('%s is not callable' % (func_name)) or sys.exit(2)
        for arg in ((len(get_args(func)) != 1) and [args] or get_input(args)):
            ret = func(*arg)
            if ret != None:
                print(ret)
    def help(self, msg=None):
        def format_args(k_list, v_list):
            return ', '.join(len(v_list) + i >= len(k_list) and '%s=%s'%(k, v_list[len(v_list) + i -len(k_list)]) or '%s'%(k)
                             for i, k in enumerate(k_list))
        if msg: print(msg)
        for f in self:
            sig = inspect.signature(f)
            print('%s(%s):\n\t%s'%(f.__name__, sig, f.__doc__))

uf = UF()

@uf
def str2int(str):
    '''convert '1234' to binary integer'''
    sys.stdout.write(struct.pack("@q", int(str)))
@uf
def str2ts(str):
    '''convert str to ts(seconds), default format: "2013-06-18 13:15:00" '''
    base = str.split('.')
    if len(base) > 1:
        base, ms = base
    else:
        base, ms = base[0], 0
    return int(time.mktime(time.strptime(base, '%Y-%m-%d %H:%M:%S'))) * 1000000 + int(ms)

@uf
def ts2str(ts):
    '''convert ts(seconds) to str # date -d @1470987270'''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)/1e6))

@uf
def str2ip(addr):
    '''convert ip to int'''
    return struct.unpack("!I", socket.inet_aton(addr))[0]

@uf
def ip2str(ip):
    '''convert ip(int) to str(127.0.0.1)'''
    return socket.inet_ntoa(struct.pack('I',int(ip)))

@uf
def dos2unix():
    r'''convert '\r\n' to '\n' '''
    return sys.stdin.read().replace('\r\n', '\n')

@uf
def clock():
    "output timestamp every second"
    while True:
        sys.stdout.write('%d\n'%(time.time() * 1000000))
        sys.stdout.flush()
        time.sleep(1)

@uf
def encode_msg(x):
    if not sys.stdout.isatty():
        sys.stdout.write(struct.pack("@i", len(x) + 4))
    sys.stdout.write(x)
    sys.stdout.flush()

@uf
def binary_format(x):
    '''convert int to binary format string'''
    return '{0:064b}'.format(int(x))

@uf
def hex_format(x):
    '''convert int to binary format string'''
    return hex(int(x))

@uf
def int2km(x):
    if x < 1<<10:
        return '%3dB'%(x)
    if x < 1<<20:
        return '%3dK'%(x>>10)
    if x < 1<<30:
        return '%3dM'%(x>>20)
    return '%3dG'%(x>>30)

@uf
def time_filt(line):
    '''cat log/observer.log | conv.py time_filt'''
    def parse_ts(str, ms):
        return time.mktime(time.strptime(str, '%Y-%m-%d %H:%M:%S')) + float(ms)/1000000
    return re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).(\d+)', lambda m: str(str2ts(m.group(0))), line)

@uf
def maps_filt(line):
    '''cat /proc/<pid>/maps | ./conv.py maps_filt'''
    addr_pat = '[0-9A-Fa-f]+'
    m = re.match('(%s)-(%s)'%(addr_pat, addr_pat), line)
    if not m:
        return line
    start, end = int(m.group(1),16), int(m.group(2), 16)
    return '%s %s'%(end - start, line)
    return '%s %s'%(int2km(end - start), line)

@uf
def dmesg_filt():
    '''dmesg | ./conv.py dmesg_filt'''
    start_time = time.time() - float(open('/proc/uptime').read().split()[0])
    def format_time(seconds):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))
    print(re.sub(r'(?m)^\[([0-9.]+)\]', lambda m: format_time(float(m.group(1)) + start_time), sys.stdin.read()))

@uf
def ip_filt(line):
    '''cat a.txt | conv.py ip_filt'''
    for x in re.findall('[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+', line):
        print(x)

@uf
def join():
    '''cat a.txt | conv.py join'''
    print(','.join(x.strip() for x in sys.stdin.readlines() if x.strip()))

import hashlib

@uf
def passwd(token):
    '''x./conv.py passwd yourpassword'''
    salt = 'dmhqekgkdebhjjojqnnqphkilhgnglcbocndhmfhqfgcdbpodfipcqnlcqdlcpgljqdcqoqoodpnjoqgonqbnplefcnbfbodijeljjmenihgfbeihcgfcgfmhcpjogeieqhqlkehleignnbmeddmoobclqpgjjkbpdhgfongedckhmnieqcimlpgohqekfnncehqgcmpogndhdppmpcljqghlbcelijhglhfpmminjbdenbfegbqnqpjjbiihmob'
    return hashlib.md5(salt + token).hexdigest()

@uf
def randstr(len):
    '''./conv.py randstr len'''
    return ''.join(chr(random.randint(ord('a'),ord('z'))) for i in range(int(len)))

@uf
def rand01(len):
    '''./conv.py rand01 len'''
    return ''.join(chr(random.randint(ord('0'),ord('1'))) for i in range(int(len)))

@uf
def unhex(line):
    '''cat data | ./conv.py hex2str #hex-file format: 313237'''
    return binascii.unhexlify(''.join(re.findall('([0-9a-fA-F]{2})', line)))

@uf
def encrypt(cypher):
    '''echo '...' | conv.py encrypt cypher'''
    cypher = itertools.cycle(cypher)
    for line in sys.stdin:
        print(''.join('%02x'%((ord(c) ^ ord(cypher.next()))% 256) for c in line))

@uf
def decrypt(cypher):
    '''echo '...' | conv.py decrypt cypher'''
    cypher = itertools.cycle(cypher)
    for line in sys.stdin:
        print(''.join(chr((int(c, 16) ^ ord(cypher.next()))% 256) for c in re.findall('([0-9a-fA-F]{2})', line)))

@uf
def i64encode(text):
    '''echo 1234 | conv.py i64encode'''    
    hex = '%016x'%(int(text))
    phex = re.sub('(..)', r'\\x\1', hex)
    return '%s grep -UP "%s"' % (hex, phex)


@uf
def vi64encode(text):
    '''echo 1234 | conv.py vi64encode'''
    max_v1b = (1<<7) - 1
    i = int(text)
    x = 0
    while i > max_v1b:
        x <<= 8
        x += (i & max_v1b) + (1<<7)
        i >>= 7
    x <<= 8
    x += i
    return i64encode(x)

@uf
def tenant_id(text):
    '''echo 1234 | conv.py tenant_id'''
    id = int(text)
    tenant_id, tid = id>>40, id & ((1<<40) - 1)
    return tenant_id, tid

@uf
def hex2ip(text):
    '''echo Y6EF16445C22A | conv.py trace'''
    x = re.sub('[0-9A-F]{2}', lambda x: str(int(x.group(0), 16)) + '.', text)
    if x == text:
       raise Exception('NoMatch')
    return x

def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]
@uf
def trace2ip(text):
    '''echo Y6EF16445C22A | conv.py trace2ip'''
    b = int(re.sub('(Y?)([A-Z0-9]+)(.*?)$', r'\2', text), 16)
    ip, port = b & 0xffffffff,  b >> 32
    return '%s:%d'%(ip2str(swap32(ip)), port)

@uf
def btrace_filter():
    def parse_blk(raw):
        pat = r'^\s*n,n n n ([.0-9]+) n ([A-Z]+) [A-Z]+ '.replace('n', r'\d+').replace(' ', r'\s+') + r'(\d+ [+] \d+)'
        return re.findall(pat, raw, re.M)
    def parse_blktrace(file):
        for line in file:
            for i in parse_blk(line):
                yield i
    def btrace_filter(file):
        start_ev = {}
        for ts, op, pos in parse_blktrace(file):
            if op == 'A':
                start_ev[pos] = float(ts)
            elif op == 'C':
                if pos not in start_ev:
                    continue
                print('%f\t%s\t%f'%(start_ev[pos], pos.replace(' ', ''), float(ts) - start_ev[pos]))
                del start_ev[pos]
    btrace_filter(sys.stdin)
# def obdatetime2sql(line):
#     '''cat clog.txt | ./conv.py obdatetime2sql  # 2016-08-05 19:44:02.0 1470397442000000 => 2016-08-05 19:44:02.0'''
#     obdatetime_pat = '(?m)(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d+) \d+$'
#     return re.sub(obdatetime_pat, '\'\\1\'', line),

@uf
def split_by_size(group_size=4):
    '''echo 'abcdefghijk' | ./conv.py split_by_size 4  # output: abcd efgh ijk'''
    gsize = int(group_size)
    for line in sys.stdin:
        print(' '.join(line[i:i+gsize] for i in range(0, len(line), gsize)), end='')
@uf
def mark(match_file):
    '''cat a.log | cat a.txt |./conv.py mark line2mark.txt | sed '/###/s/from/to/' '''
    match_list = open(match_file).read().split('\n')
    def is_match(line):
        return any(m in line for m in match_list)
    for line in sys.stdin:
        if is_match(line):
            print('###%s'%(line))
        else:
            print(line)

def txt2tab(txt):
    tab = [line.split() for line in txt.split('\n')]
    return [row for row in tab if len(row) > 1]

@uf
def grender():
    '''echo '1 2' | ./grender.py |dot -T png -o a.png #grender provides a python scripts translate txt file to dot file'''
    tab = txt2tab(sys.stdin.read())
    return 'digraph G {\n%s\n};'%(''.join('    %s->%s;\n'%(n1, n2) for n1, n2 in tab))
 
@uf
def reverse():
    '''echo -e 'a\\nb' | ./conv.py reverse'''
    for line in reversed(sys.stdin.readlines()):
        print(line, end='')

@uf
def trunc_space():
    '''cat a.txt | ./conv.py strip_space'''
    content = sys.stdin.read()
    content = re.sub('(?m)[ \t]+$', '', content)
    sys.stdout.write(content.strip())

@uf
def replace(f):
    '''cat a.txt | ./conv.py replace replace-kv-pair.txt'''
    kv = dict(re.findall('^([^\t]+)\t(.+)$', open(f).read(), re.M))
    print(re.sub(r'\w+', lambda m: kv.get(m.group(0), m.group(0)), sys.stdin.read()))

def eval_expr(x):
    return eval(x)

@uf
def grep_src_from_url(x):
    '''./conv.py grep_src_from_url 4018'''
    x = x.split()[0]
    #return os.popen('grep -w -rni "%s" ~/m/dict 2>/dev/null |head -10 2>/dev/null'%(x)).read()
    dict_url = 'http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/dict.tar.bz2'
    return os.popen('''curl -m 1 -s %s | tar jx  -O | grep -w "%s" || true ''' %(dict_url, x)).read()

@uf
def grep_src(x):
    '''./conv.py grep_src 4018'''
    def safe_get_hex(x):
        try: return hex(int(x))[2:]
        except: return None
    x = x.split()[0]
    hex_str = safe_get_hex(x)
    pat = x
    if hex_str: pat = r'%s\|0x%s\|0x%s'%(x, hex_str, hex_str.upper())
    return os.popen('grep -w -rnI "%s" ~/m/dict 2>/dev/null |head -10 2>/dev/null'%(pat)).read()

def render_table(table):
    def render_html(table):
        def render_row(row): return ''.join('<td><pre>%s</pre></td>'%(cell.replace('\n', '<p>\n')) for cell in row)
        return '<table style="border:1px solid black; border-collapse: collapse">%s</table>'%('\n'.join('<tr>%s</tr>'%(render_row(row)) for row in table))
    def render_txt(table):
        return '\n'.join(':\t'.join(row) for row in table)
    if os.getenv('term') == 'html':
        return render_html(table)
    return render_txt(table)

@uf
def guess(x=None):
    '''./conv.py guess 100000'''
    if x == None and not sys.stdin.isatty():
        x = sys.stdin.read()
    flist = [eval_expr, ts2str, str2ts, ip2str, str2ip, hex_format, trace2ip, tenant_id, grep_src]
    def try_call(f, x):
        try:
            r = f(x)
            if not r: return None
            return f.__name__, str(r)
        except:
            # print(traceback.format_exc())
            return None
    return render_table(filter(None, (try_call(f, x) for f in flist)))

import base64
@uf
def b64(x):
    '''./conv.py b64 TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJ5IGhpcyByZWFzb24sIGJ1dCAuLi4='''
    return base64.b64decode(x)

@uf
def shift_addr(x):
    '''cat a.txt | ./conv.py shift_addr -0x7f5bad641000'''
    return re.sub('([0-9a-f]{6,})', lambda m: hex(int(m.group(1), 16) + int(x, 16)), sys.stdin.read())

if __name__ == '__main__':
    len(sys.argv) >= 2  or uf.help() or sys.exit(1)
    if len(sys.argv) == 2 and not uf.get(sys.argv[1]):
        sys.argv.insert(1, 'guess')
    uf.call(sys.argv[1], sys.argv[2:])
