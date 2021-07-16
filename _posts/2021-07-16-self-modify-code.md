---
layout: post
title: "self modifing code"
---


# 是否需要invalide指令cache
[x86不需要](https://stackoverflow.com/questions/10989403/how-is-x86-instruction-cache-synchronized)
[arm需要](https://community.arm.com/developer/ip-products/processors/b/processors-ip-blog/posts/caches-and-self-modifying-code)

# 使用绝对地址还是相对地址
x86上使用绝对地址有两种方法: 一种是把地址放入一个寄存器；另一种是push地址，然后ret.

[推荐使用相对地址](https://reverseengineering.stackexchange.com/questions/19459/calculation-of-jmp-address-through-subtraction)

