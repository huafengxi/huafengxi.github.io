---
layout: post
title: "ssh tunnel"
---

ssh tunnel的概念可以man ssh, 搜索`-R`,`-D`参数理解下面两个命令的意思

# ssh建立隧道
## 如果ssh client足够新
一条命令可以建立socks代理
```
ssh 172.16.31.131 -R 8123
```
## 如果ssh client比较老
需要分两步
`ssh root@172.16.31.131 -R :8123:127.0.0.1:8123 -f -N`
执行成功后在172.16.31.131上执行`netstat -tnlp |grep 8123`应该可以看到sshd listen在8123端口

`ssh 127.0.0.1 -D :8123 -f -N`
执行成功后在跳板机上执行`netstat -tnlp | grep 8123`应该可以看到sshd listen在8123端口.

# 使用代理
## 配置curl代理
`ALL_PROXY=socks5h://127.0.0.1:8123 curl -s www.baidu.com`
如果不生效，可以尝试kill跳板机和172.16.31.131上listen在8123端口的sshd进程，然后重来。

## 配置ssh代理
确保`sock_proxy.py`,`socks.py`在`~/bin`目录下, 并且`export PATH=~/bin:$PATH`
`sock_proxy.py`和`socks.py`可以从以下url下载

-   <http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/sock_proxy.py>
-   <http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/socks.py>


然后修改~/.ssh/config文件 添加如下的行: 
```
    Host gitlab.alibaba-inc.com github.com
        User yuanqi.xhf
        IdentityFile ~/.ssh/id_dsa.yq
        ProxyCommand sock_proxy.py socks5h://127.0.0.1:8123 %h %p
```
