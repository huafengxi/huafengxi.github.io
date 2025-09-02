#!/bin/env python2
'''
git show 8ebb01d5423f |grep '^+' |tail +1 | ./update-codeowner.py CODEOWNERS > CODEOWNERS.new
'''

import sys
import re

def help(): print __doc__
len(sys.argv) == 2 or help() or sys.exit(1)

mappings = dict(re.findall('^[+]([^ ]+) (.*)$', sys.stdin.read(), re.M))
print mappings
for ln in file(sys.argv[1]):
    k, v = ln.strip().split(' ', 1)
    print '%s %s'%(k, mappings.get(k, v))
