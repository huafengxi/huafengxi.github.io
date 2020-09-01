---
layout: post
title: why lfench
---

# ref
[ignificance-of-the-x86-lfence-instruction](https://hadibrais.wordpress.com/2018/05/14/the-significance-of-the-x86-lfence-instruction/)
[知乎](https://www.zhihu.com/question/29465982)

# 总结
如果把lfence理解为load fence，那么lfence确实基本没有用，但是lfence不仅会等load操作完成，而是会等所有的指令都local完成,
local完成的含义是写不一定全局可见，这也是lfence和mfence的差别

# 例子1
lfence加在rdtsc前后，可以让rdtsc计时更加准确。

# 例子2
让load和non temporal write排序
```
non temporal write
lfench
load
```

# 例子3
虽然，x86 memory consistency要求load-to-load order，但实际执行中，这个order并不被保证。如果程序员确实希望保证线程内的load-to-load order，那就只能借助lfence这种指令的。
答主在实验室研究中倒会偶尔用到，用它保证访存指令在memory system中执行的顺序。
