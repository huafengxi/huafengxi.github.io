---
layout: post
title: "gcc -march -mtune -mcpu"
---

# reference
https://community.arm.com/developer/tools-software/tools/b/tools-software-ides-blog/posts/compiler-flags-across-architectures-march-mtune-and-mcpu

# march vs mtunu
1. `march`指定编译器可用的指令集和寄存器。
2. `mtune`指定指令执行时间，用于编译器对指令调序。
为什么要有这两个参数？
可以用`march`指定一个指令集，保证一定的适用范围。用`mtune`指定微体系结构，保证在某一系列的cpu上运行更好。

# x86
在x86下面`-mcpu`已经作废，它等价于`-mtune`; `-march`隐含`-mtune`.

x86的最佳实际是指定`-march=native`, x86上之所以能这么做是因为指令集相对标准.

# arm
arm的最佳实践是指定`-mcpu=native`, 不要指定`-march`和`-mtune`

arm不能通过指定`march`获得最佳性能，是因为arm的指令集是各种混搭，很多arm cpu同会把高版本的指令集的扩展往低版本cpu上移植，只指定`march`没办法获得最佳性能。
