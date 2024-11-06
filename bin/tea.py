#!/usr/bin/env python2
'''
cat $r/a | ./tea.py stdin ...  # execute bin from stdin
tea=$r/foo.tar.gz ./tea.py ... # execute cmd by LD_PRELOAD underlay
./tea.py --pack=$r/foo.tar.gz ... # execute cmd by LD_PRELOAD underlay
'''
import sys
import re
import copy
import os, stat
import subprocess
import tempfile
import logging

def mkfd():
    fd, name = tempfile.mkstemp()
    os.unlink(name)
    return fd

def proc_path(fd):
    return '/proc/self/fd/%d'%(fd)

def prepare_file(content):
    fd = mkfd()
    try:
        os.write(fd, content)
        os.fchmod(fd, stat.S_IRUSR | stat.S_IXUSR)
        return proc_path(os.open(proc_path(fd), os.O_RDONLY))
    finally:
        os.close(fd)

import urllib2
def gettar(url):
    return urllib2.urlopen(url).read()

def get_host(url):
    m = re.match('(.+)/', url)
    if m: return m.group(0)
    return url

import tarfile
import gzip
from cStringIO import StringIO
def untar(targz):
    unzip_content = gzip.GzipFile(fileobj=StringIO(targz)).read()
    tar = tarfile.TarFile(mode='r', fileobj=StringIO(unzip_content))
    return [(x.name, tar.extractfile(x).read()) for x in tar if x.isreg()]

def help():
    print __doc__
not (len(sys.argv) == 1 and sys.stdin.isatty()) or help() or sys.exit(1)
tea_url = os.getenv('tea')
if sys.argv[1].startswith('--pack='):
   tea_url = sys.argv[1][7:]
   sys.argv.pop(1)
len(sys.argv) > 1 or help() or sys.exit(2)
bfile, args = sys.argv[1], sys.argv[1:]
logging.debug("tea=%s bfile=%s args=%s", tea_url, bfile, args)
if tea_url:
    fmap_list = [(name, prepare_file(content)) for name, content in untar(gettar(tea_url))]
else:
    fmap_list = []
if bfile == 'stdin':
    fmap_list.append(('stdin', prepare_file(sys.stdin.read())))
fmap_path = prepare_file(''.join('%s %s\n'%(k, v) for k, v in fmap_list))
fmap_dict = dict(fmap_list)

p = subprocess.Popen(['/usr/bin/which', bfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pout = p.communicate()[0]
if 0 != p.wait():
    bfile = fmap_dict.get(bfile)
else:
    bfile = pout.strip()
if not bfile:
    raise Exception("bin not found: bfile={}".format(bfile))

env = copy.copy(os.environ)
env.update(LD_LIBRARY_PATH='lib:%s'%(os.getenv('LD_LIBRARY_PATH', '')))
if tea_url:
    uso_url = get_host(tea_url) + '/u.so'
    try:
        underlay_so = prepare_file(urllib2.urlopen(uso_url).read())
    except Exception as e:
        raise Exception("fail to get u.so: %s url=%s"%(e, uso_url))
    env.update(LD_PRELOAD=underlay_so, FMAP=fmap_path)
os.execve(bfile, args, env)
