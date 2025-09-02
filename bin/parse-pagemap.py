#!/bin/env python2
'''
./pagemap.py pid
'''

import sys
import re
import struct

def help(): print __doc__
len(sys.argv) == 2 or help() or sys.exit(1)

pid = sys.argv[1]
fd = open('/proc/%s/pagemap'%(pid), 'rb')
for s, e in re.findall('^([0-9a-f]+)-([0-9a-f]+)', open('/proc/%s/maps'%(pid)).read(), re.M):
    ps, pe = int(s,16)>>12, int(e,16)>>12
    fd.seek(ps * 8)
    data = fd.read((pe - ps) * 8)
    if not data: continue
    for idx in range(pe - ps):
        pte, = struct.unpack_from('Q', data, idx * 8)
        print '%010x %x'%((ps+idx)<<12, pte)