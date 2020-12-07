---
layout: post
title: "why user defined partition"
---

# reference
[oracle user defined partition](https://blog.csdn.net/thy822/article/details/80262668)


用户定义分区本质是为了传递一些额外信息给DBMS，从而实现更好的优化。

从DBMS提供的功能看，优化的对象初略分为DML和DDL(以及其他管理命令)
具体例子包括:
1. 冷数据和热数据分开，放到不同的partition，从而让不同的partition放到不同的磁盘上。
2. partition pruning优化SQL扫描的数据范围。

## partition pruning
目的是为了优化性能，关键是在哪些情况下必须借助partition的概念才能实现更好的过滤，也即借助partition能实现比btree更好的过滤。

一种情况是分区键并不是主键的组成部分, 这时根据分区键做的过滤显然无法通过主键的btree索引完成。

但即使分区键是主键的一部分，假如有两列 `<a,b>`, btree的范围过滤无法表达`a > 0 && b > 0` 的过滤条件，借助合适的分区规则是可以的。

同时，还要明白，分区裁剪需要结合局部索引才有用，否则，分区裁剪和另外建一个索引没有什么差别，起不到过滤的作用。


