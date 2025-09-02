#!/usr/bin/env python2
'''
./j.py cmd # submit to any host
./j.py 'cmd...' host1 'cmd...' host2  # submit sequence job
'''
import sys
import os
import itertools
import time

def help(): print __doc__
len(sys.argv) > 1 or help() or sys.exit(1)

os.system('rm -rf ~/j && mkdir -p ~/j')
id_gen = itertools.count(int(time.time() * 1000))
def write_job(id, cmd, host='any', deps=''):
    print 'write_job: {} {} host={} deps='.format(id, cmd, host, deps)
    with open(os.path.expanduser('~/j/{}.{}'.format(id, host)), 'w') as f:
        f.write('### deps: {}\n'.format(deps))
        f.write('{}\n'.format(cmd))

if len(sys.argv) == 2:
    write_job(id_gen.next(), sys.argv[1])
else:
    deps = ''
    for i in range(1, len(sys.argv), 2):
        cmd, host = sys.argv[i], sys.argv[i+1]
        cur_id = id_gen.next()
        write_job(cur_id, cmd, host=host, deps=deps)
        deps = str(cur_id)
ssh_host = os.getenv('pub_ssh_host')
if ssh_host:
    os.system('rsync -avz --progress ~/j/ {}:p/j'.format(ssh_host))
