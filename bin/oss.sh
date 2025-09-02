#!/usr/bin/env bash

if [ -n $HAP_PROXY ]; then
    export ALL_PROXY=$HAP_PROXY
fi
OSS=${OSS:-oss://051915} # http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/


function help() {
    echo "Usage:"
    echo "oss.sh ls # oss.sh read /"
    echo "oss.sh rm a.txt"
    echo "oss.sh put bin/observer # date | oss.sh put date.txt"
    echo "oss.sh get observer     # oss.sh get date.txt | cat" 
    echo "oss.sh putz bin/observer"
    echo "oss.sh getz observer"
    echo "oss.sh gete observer bin # download && chmod && mv"
}

if [ "$(uname)" == "Darwin" ]; then
    readlink=greadlink
else
    readlink=readlink
    function zstd() {
        python2 <(curl -s $r/hap.py) tea.py --pack=$r/zstd.tar.gz zstd $@
    }
fi

if [[ $OSS == "none" ]]; then
    function ls() {
        echo "# nowhere to list $1"
    }
    function do_get() {
        echo "# nowhere to get $1"
    }
    function do_cat() {
        echo "# nowhere to cat $1"
    }
    function do_put() {
        echo "# nowhere to put $1"
    }
elif [[ $OSS == ssh://* ]]; then
    prefix='ssh://'
    ip_port=${OSS#$prefix}
    read ip port < <(echo $ip_port|sed -e 's/:/ /')
    port=${port:-22}
    function ls() {
        ssh -p $port  $ip ls p/$1
    }
    function do_get() {
        rsync -e "ssh -p $port"  --progress $ip:p/$1 .
    }
    function do_cat() {
        ssh -p $port  $ip cat p/$1
    }
    function do_put() {
        rsync -e "ssh -p $port" --progress $1 $ip:p/$2
    }
elif [[ $OSS == http://* ]]; then
    curl_cmd='curl -s'
    function do_get() {
        $curl_cmd $OSS/$1 -o $1
    }
    function do_cat() {
        $curl_cmd $OSS/$1
    }
    function do_put() {
        $curl_cmd -X POST "$OSS/$2?v=upload&post=file" --data-binary @$1
        echo ''
    }
elif [[ $OSS == oss://* ]]; then
    oss_base=$OSS
    nfilter='s#.*oss://[0-9]*/\([a-zA-Z0-9._-]*\).*#\1#p'
    function ls() {
        $oss_cmd listallobject $OSS/$1 | sed -n $nfilter
    }
    function rm() {
        for i in "$@"; do
            if [[ $i == */ ]]; then
                $oss_cmd deleteallobject $OSS/${i%/*}
            else
                $oss_cmd rm $OSS/$i
            fi
        done
    }
    function do_get() {
        $oss_cmd multiget --thread_num=10 $OSS/$1 $1
    }
    function do_cat() {
        $oss_cmd cat $OSS/$1 2>/dev/null
    }
    function do_put() {
        $oss_cmd multiupload --thread_num=40 $1 $OSS/$2
    }
fi
function read() {
    if [[ $1 == */ ]]; then
        do_ls $1
    else
        do_cat $1
    fi
}

function write() {
    echo 'write'
}

function get() {
    if [ -t 1 ]; then
        do_get $1
    else
        do_cat $1
    fi
}

function put() {
    local_file=$1
    [ -t 0 ] || cat > $local_file
    full_remote_file=${2-$1}
    remote_file=$(basename $full_remote_file)
    do_put $local_file $remote_file
}

function getz() {
    rfile=$1
    get $rfile.zstd
    time zstd -d -f $rfile.zstd -o $rfile
}

function putz() {
    lfile=$1
    [ -t 0 ] || cat > $lfile
    time zstd --fast -T -f $lfile -o $lfile.zstd
    put $lfile.zstd
}
real_file=$($readlink -f $0)
base_dir=`dirname $real_file`
method=${1:-help}
shift
ulimit -c unlimited
if [ "$method" != "help" ]; then
    false && set_exit_trap
fi
$method $*
