#!/bin/env python2
'''
cat a.cpp | ./code.py sort > a.cpp.sort # sort code block by first line
# ref: https://huafengxi.github.io/2021/03/24/google-translate-comment.html
cat a.cpp | ./code.py dump_comment
cat a.cpp | ./code.py update_comment  mapfile >a.cpp.new
cat a.txt | ./code.py none_ascii
./code.py update_copyright a.h a.cpp
./code.py cmake xxx/xxx/xxx.cpp # print correct cmake command
./code.py filt_warning file.list # filt warning only generate by file in `file.list`
./code.py class_tag A  src_dir # print struct or class
./code.py fix_class_tag A src_dir # fix struct or class tag
'''
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import itertools
import re
import os, os.path

def split_code_block(text):
    return re.findall('^\S[^\n]+::.*?^}', text, re.M|re.S)

def sort_by_block_head(text):
    def first_line(lines): return lines.split('\n', 1)[0]
    return '\n//// blocks ////\n'.join(sorted(split_code_block(text), key = lambda x: first_line(x)))

def sort():
    print sort_by_block_head(sys.stdin.read())

c_style_comment = '/[*].+?[*]/'
cpp_style_comment = '//.+?$'
comment_regexp = '(?:%s)|(?:%s)'%(c_style_comment, cpp_style_comment)
def clean_comment(line):
    m = re.match('^ [/*]* (.*?) [/*]* $'.replace(' ', '\s*'),  line)
    return m and m.group(1) or line
def dump_comment():
    text = sys.stdin.read()
    for m in re.findall(comment_regexp, text, re.M|re.S):
        for line in m.split('\n'):
            print clean_comment(line)

def build_dict(txtfile):
    lines = [line.strip() for line in file(txtfile)]
    key_lines, value_lines = itertools.islice(lines, 0, None, 2), itertools.islice(lines, 1, None, 2)
    return dict(itertools.izip(key_lines, value_lines))
def update_comment(mapfile):
    d = build_dict(mapfile)
    text = sys.stdin.read()
    def replace_one_line_comment(line):
        pure_comment = clean_comment(line)
        new_comment = d.get(pure_comment, None)
        return line.replace(pure_comment, new_comment) if new_comment else line
    def update_comment_func(m):
        return '\n'.join(replace_one_line_comment(line) for line in m.split('\n'))
    print re.sub(comment_regexp, lambda m: update_comment_func(m.group(0)), text, flags=re.M),

def none_ascii():
    for line in sys.stdin:
        if re.search(r'[^\x00-\x7F]', line):
            print line,

copyright_header = '''
// Copyright (c) 2021 Ant Group CO., Ltd.
// OceanBase is licensed under Mulan PubL v1.
// You can use this software according to the terms and conditions of the Mulan PubL v1.
// You may obtain a copy of Mulan PubL v1 at:
//            http://license.coscl.org.cn/MulanPubL-1.0
// THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
// EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
// MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
// See the Mulan PubL v1 for more details.
'''
def update_copyright(*file_list):
    def remove_header_comment(text):
        return re.sub('^(//[^\n]*\n)*', '', text)
    def update_file(path, text):
        with open(path, 'w') as f:
            f.write(text)
    def update_one_file_copyright(f):
        new_text = copyright_header.strip() + '\n\n' + remove_header_comment(file(f).read())
        update_file(f, new_text)
    for f in file_list:
       update_one_file_copyright(f)

def locate_innermost_dir(path, file):
    while path:
        path = os.path.split(path)[0]
        if os.path.exists(os.path.join(path, file)):
            return path
    return ''

def cmake(path):
    cmake_dir = locate_innermost_dir(path, 'CMakeLists.txt')
    if cmake_dir:
        return 'make -C $build_dir/%s %s.o'%(cmake_dir, path[len(cmake_dir) + 1:].replace('.cpp', ''))

import subprocess
def class_tag(C, *src_dir):
    grep_cmd = '''grep -rI 'struct {0}\|class {0}' {1}'''.format(C, ' '.join(src_dir))
    output = subprocess.Popen(grep_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
    m = re.search('(struct {0}|class {0})\s'.format(C), output + ' ')
    return m.group(1)

def fix_class_tag(C, *src_dir):
    print '# fix {}'.format(C)
    tag = class_tag(C, *src_dir)
    mismatch_tag = ('struct {}' if tag.startswith('class') else 'class {}').format(C)
    print '# mismatch_tag: {} right_tag: {}'.format(mismatch_tag, tag)
    sed_cmd = '''grep -rIl '{0}' {2}| xargs sed -i 's/{0};/{1};/' '''.format(mismatch_tag, tag, ' '.join(src_dir))
    return subprocess.call(sed_cmd, shell=True)

def filt_warning(file_list):
    file_list = [os.path.basename(f.strip()) for f in file(file_list).readlines()]
    def filt_one_line(line):
        for f in file_list:
            if f in line: return True
    ctx = 0
    for line in sys.stdin:
        if ctx > 0:
            print line,
            if 'note:' in line:
                ctx += 1
            else:
                ctx -= 1
        if filt_one_line(line):
            print line,
            ctx = 2

def help(): print __doc__
len(sys.argv) >= 2  or help() or sys.exit(1)
func = globals().get(sys.argv[1])
callable(func) or help() or sys.exit(2)
ret = func(*sys.argv[2:])
if ret != None:
    print ret

