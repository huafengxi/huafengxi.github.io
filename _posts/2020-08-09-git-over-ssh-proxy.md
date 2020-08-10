---
layout: post
title: git over ssh proxy
---

# setup ssh proxy
from local host
```
ssh remote_host -R 8123 -f -N
```

# test proxy
from remote host
```
ALL_PROXY=socks5://127.0.0.1:8123 curl -s www.baidu.com
```

# ~/.ssh/config.py
```
Host github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:8123 %h %p
```

# get nc
download from [github](https://github.com/huafengxi/bin-mirror/blob/master/nc.x86_64)
