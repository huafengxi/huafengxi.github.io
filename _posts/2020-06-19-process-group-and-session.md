---
layout: post
title: "What is Pocess Group and Session?"
---

# process group and session
一个session包含一个或多个process group，一个process group包含一个或多个process。

`ps j`可以看到pgid和sid。

当我们在bash里执行`cat a.txt | grep xxx`时，通过管道连接的多个进程就会形成一个新的process group.

# syscall
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

# daemonize
```
if fork(): os.exit()
os.setsid()
```
这样让子进程独立在另一session里，这样就和当前session独立了。

# double forck?
daemonize并不需要double fork.
double fork的目的是确保daemon进程不能再获取control tty。

# ref
+ [stack overflow](https://stackoverflow.com/questions/881388/what-is-the-reason-for-performing-a-double-fork-when-creating-a-daemon)
+ [process concept](https://www.win.tue.nl/~aeb/linux/lk/lk-10.html)
