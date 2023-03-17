#!/bin/bash
function sys_stat() {
    ip=`hostname -i`
    free_mem=`free -g |sed -n '3p' |awk '{print $4}'`
    total_mem=`free -g |sed -n '2p' |awk '{print $2}'`
    core_num=`lscpu -p |grep -v '^#' |wc -l`
    disk_num=`df -h|grep '^/dev/' |wc -l`
    home_free=`df -h /home |sed -n '2p' |awk '{print $4}'`
    netdev=`ifconfig |grep '^eth' |awk '{print $1}'`
    #netspeed=`sudo ethtool eth0 |grep Speed | awk '{print $2}'`

    echo -e "ip: $(hostname -i); mem: $free_mem/$total_mem; cpu_num: $core_num; net: $netdev $netspeed; disk_num: $disk_num; home_free: $home_free;"
    echo -e "uname: $(uname -r); uptime:$(uptime)"
    echo -e "clock: $(cat /sys/devices/system/clocksource/clocksource0/current_clocksource); hugepage: $(cat /sys/kernel/mm/redhat_transparent_hugepage/enabled);"
}

sys_stat
