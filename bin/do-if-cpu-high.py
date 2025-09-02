import time, os

def get_accum_cpu_idle():
    with open('/proc/stat') as f:
       return int(f.readline().split()[4])

cpu_num = os.sysconf('SC_NPROCESSORS_ONLN')
def get_cpu_idle():
    last_ts, last_idle = time.time(), get_accum_cpu_idle()
    while True:
        time.sleep(1)
        cur_ts, cur_idle = time.time(), get_accum_cpu_idle()
        yield (cur_idle - last_idle) /(cur_ts - last_ts)/cpu_num
        last_ts, last_idle = cur_ts, cur_idle

for idle in get_cpu_idle():
    print 'idle=%d'%(idle)
    if idle < 10:
        print 'cpu high, do script'
        os.system('sh ./do-perf-record.sh')