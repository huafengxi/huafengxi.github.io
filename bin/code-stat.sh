#!/bin/bash

help() {
    echo "./code-stat.sh sum"
    echo "./code-stat.sh func_grep"
    echo "./code-stat.sh big_func bin/observer"
    echo "./code-stat.sh big_var bin/observer"
    echo "./code-stat.sh all_type bin/observer"
    echo "./code-stat.sh type_size bin/observer"
}

sum() {
    if [ -n "$*" ]; then
        echo "sum for $*"
        dlist=$*
    else
        echo "no given dir, sum for subdir of ."
        dlist=`find . -maxdepth 1 -and -type d`
    fi
    cfg_cnt
    table_cnt
    for d in $dlist; do
        file_cnt=`file_cnt $d`
        line_cnt=`sloc_dir $d`
        const_cnt=`const_count_dir $d`
        echo -e "### dir=$d\tfile_cnt=$file_cnt\tline_cnt=$line_cnt\tconst_cnt=$const_cnt"
        top_file $d
    done
}
file_list() {
    find  $1 -name '*.h' -or -name '*.cpp' -or -name '*.cc'
}
file_cnt() {
    file_list $1 | wc -l | xargs
}
sloc_dir() {
    files=`file_list $1`
    if [ -n "$files" ]; then wc -l $files | tail -1|awk '{print $1}'; fi
}

const_count_dir() {
    grep -rI '\(^const int\)\|\(const static int\)' $1 |wc -l | xargs # xargs to trim white space
}

cfg_cnt() {
    cfg_file=`find . -name ob_server_config.h`
    total_cnt=`grep DEF_ $cfg_file|wc -l | xargs`
    test_cnt=`sed -ne '/ifdef CLOG_MODULE_TEST/,$ p' $cfg_file | grep DEF_ |wc -l |xargs`
    echo "### cfg: total=$total_cnt test=$test_cnt"
}

table_cnt() {
    def_file=`find . -name ob_inner_table_schema_def.py`
    echo '### table_count:'
    grep "table_type = '" share/inner_table/ob_inner_table_schema_def.py |awk -F '= ' '{print $2}' |sort | uniq -c
}

top_file() {
    files=`file_list $1`
    if [ -n "$files" ]; then
        wc -l $files | sort -k 1 -n -r | head -5
    fi
}

func_grep() {
    if [ -z "$1" ]; then
        echo "need specify match pattern"
        return
    fi
    echo "match by '$1'"
    files=`grep -rI "$1" . -l`
    for f in $files; do
        echo "file: $f"
        grep "$1" $f -A 10 | grep.py indent_collapse | grep "$1"
    done
}

big_func() {
 readelf -sW $1 | awk '$4 == "FUNC" { print }' | sort -k 3 -n -r | head -n 50 | c++filt
}

big_var() {
 readelf -sW $1 | awk '$4 == "OBJECT" { print }' | sort -k 3 -n -r | head -n 50 | c++filt
}

all_type() {
  gdb $1 -n -q --batch -ex 'info types ^oceanbase::' | grep '^oceanbase::.*;$' | sort | uniq
}

type_size() {
  all_type $1 | sed 's/\(.*\);/printf "XXXX \1\\t%d\\n", sizeof(\1)/' | gdb $1 -n -q | sed 's/(gdb) //g' |  sed -n 's/XXXX //p' | sort -k 2 -n -r
}


method=${1:-help}
shift
ulimit -c unlimited
if [ "$method" != "help" ]; then
    false && set_exit_trap
fi
$method $*

