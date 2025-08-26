* install
r7=https://huafengxi.github.io && . <(curl -s $r7/setup.sh)
alias sudoi='sudo python /dev/fd/0 <&7' # if you need sudo

* inspect package
i __pack__.ls bin        # list all packed scripts
i __pack__.read pack.py  # cat script source
i __doc__

* guess number meaning
i conv.py 13948891 # guess input as ip, timestamp, errcode

* pstack group
cat a.ps | i pstack.py # group pstack

* bind cpu
sudoi bind-cpu.py irq eth # show eth irq binding

* dedup log
cat log/observer.log | i grep.py log_reduce # remove duplicate log

* log stat
grep 'slow query' log/observer.log | i grep.py stat 'total_timeu=$N'

* extract number
grep 'slow query' log/observer.log | i grep.py find 'total_timeu=$N'

* process data by SQL
seq 10 | i tsql.py 'select plt("a.png", c1) from t1' # execute sql, need sqlite and matplotlib

* cmd dispatch
i pdo.py ssh -T @hosts.list hostname
cat a.sh | i pdo.py ssh -T @hosts.list # execute multiple cmd
i sshpass.py ip.list  # get through ssh
