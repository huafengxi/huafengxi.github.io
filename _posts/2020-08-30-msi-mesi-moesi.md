---
layout: post
title: MSI MESI MOESI
---

# 参考
[mesi](https://en.wikipedia.org/wiki/MESI_protocol)

# 为什么要MESI
如果是MSI，会有如下的bad cace

考虑一个多进程的系统，每个进程访问的内存大部分都是独占的，一个进程第一次读取一个cache line，会被标记为S状态，接下来要修改，需要做一个“总线广播”，
从S转到M状态，但是这一步广播很可能是无意义的，因为绝大部分情况下，你读取的内存就是被你独占的。


MESI是怎么处理上述case的呢？第一次读取一个memblock，会执行一次“总线广播”，如果其它processoer的cache不包含这个block，那么就可以把cache line标记为E。

# 为什么要MOESI
MESI有个缺陷，就是dirty cache line不能被transfer给其它的processor，如果cache transfer的速度大于flush到内存的速度，那么选择cache transfer会比flush cache更合算。
MOESI引入O（owned)状态就是为了解决这个问题。O状态的cache line可以被其它processoer共享，同时它也是被修改的状态，如果要淘汰，就必须要flush到内存。
