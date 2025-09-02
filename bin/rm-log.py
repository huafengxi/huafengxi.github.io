#!/bin/env python2
'''
keep_time=1440 keep_space=4096 ./rm-log.py <dir-list> # keep 1440min 4096M
'''
import os, os.path
import sys
import time

def get_file_list(path):
    try:
        return [os.path.join(path, f) for f in os.listdir(path)]
    except OSError as e:
        print e
        return []

def get_file_list2(path_list):
    return reduce(lambda x,y: x+y, map(get_file_list, path_list), [])

def du(path):
    try:
        return sum(os.path.getsize(f) for f in os.listdir(path) if os.path.isfile(f))
    except OSError as e:
        print e
        return 0

def du2(path_list):
    return sum(map(os.path.getsize, get_file_list2(path_list)))

def delete_log(path_list, time_limit, space_limit):
    path_list = filter(os.path.exists, path_list)
    print 'delete_log: %s'%(path_list)
    sort_list = sorted([(f, os.stat(f).st_mtime) for f in get_file_list2(path_list)], key=lambda x: x[1])
    for f, mtime in sort_list:
        if du2(path_list) > space_limit or mtime < time_limit:
            print 'unlink: %s'%(f)
            os.unlink(f)
        else:
            break

def usage():
    print __doc__

if __name__ == '__main__':
    len(sys.argv) > 2 or usage() or sys.exit(1)
    time_limit = time.time() - int(os.getenv('keep_time') or "180") * 60
    space_limit = int(os.getenv('keep_space') or "4096") * 1000000
    delete_log(sys.argv[1:], time_limit, space_limit)

