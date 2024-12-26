#!/bin/bash
function start_blktrace() {
    dev=$1
    dir=`date +%%m%%d%%H%%M`
    echo "blocktrace in $dir"
    mkdir $dir
    cd $dir
    echo 'kill blktrace'
    sudo pkill blktrace
    rm $dev.blktrace* -f
    echo 'start blktrace'
    sudo blktrace -d /dev/$dev &
    echo "run cmd $*"
    $*
    echo 'kill blktrace'
    sudo pkill blktrace
}

gcore_elf() {
    echo "int main(){ char* p = 0; *p = 0;  return 0;}" | gcc -o core -xc -
}

record_perf() {
    timestamp="$(date +%Y%m%d%H%M%S)"
    echo "do perf record at $timestamp"
    perf record -a -g --call-graph=dwarf -o perf.data.$timestamp sleep 10
}

# exit trap
exit_trap () {
    local lc="$BASH_COMMAND" rc=$?
    echo "Command [$lc] exited with code [$rc]"
}

set_exit_trap() {
    trap exit_trap EXIT
    set -e
    set -o pipefail
    set -x
}

# func dispatch
real_file=`readlink -f $0`
base_dir=`dirname $real_file`
method=${1:-help}
shift
set_exit_trap
$method $*
