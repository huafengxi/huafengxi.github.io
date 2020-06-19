---
layout: post
title: "What is Pocess Group and Session?"
---

[stack overflow](https://stackoverflow.com/questions/881388/what-is-the-reason-for-performing-a-double-fork-when-creating-a-daemon)
[reference](https://www.win.tue.nl/~aeb/linux/lk/lk-10.html)

一个process属于一个process group，一个process group属于一个session。

`ps j`可以看到pgid和sid。

创建process group
```
setpgid(pid, pgid); // 让pgid=0
```
当前进程不能是session leader，否则setpgid会失败。

创建session
```
pid = setsid();
```
当前进程不能是process group leader，否则setsid会失败。

## daemonize的方法
daemonize并不需要double fork
```
if fork(): os.exit()
os.setsid()
```
这样以及让进程和当前session和当前process group脱离了。

double fork的目的是确保daemon进程不能再获取control tty。
