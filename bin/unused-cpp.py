#!/bin/env python3
'''
find src deps -name '*.h' -or -name '*.cpp' -or -name '*.c' -or -name '*.hpp' -or -name '*.ipp' -or -name '*.cxx'
'''

import sys, os

def list_files(*dirs):
    print(dirs)
    file_list = []
    for directory in dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file():
                        file_list.append(entry.name)
        else:
            print(f"Directory {directory} does not exist or is not a directory.")
    return file_list

def help(): print(__doc__)
len(sys.argv) > 1 or help() or sys.exit(1)
print(list_files(*sys.argv[1:]))

