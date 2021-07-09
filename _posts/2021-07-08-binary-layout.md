---
layout: post
title: binary tree layout
---

# heap (eytzinger layout)
```
1bits 1
2bits 2 3
3bits 4 5 6 7
4bits 8 9 10 11 12 13 14 15

left(i) = 2 * i; right(i) = 2 * i + 1
level(i) = (32 - __builtin_clz(i))
```

# block binary tree (like btree)
首先定义几个概念:
1. mini tree : btree的一个节点就是一个mini tree。
2. K : mini tree的高度
3. B : mini tree的size 

heap layout相当于把binary tree按层次输出了。 block layout是block内部是heap layout。block之间也是heap layout。

我们想把heap layout的下标变成block layout的下标，为便于叙述，我们定义以下的变量。
1. i: heap layout的下标
2. x: block layout的下标

我们的目标就是根据i计算x, 为此我们还要把i分解以下:
1. R: i的高位部分，表示mini tree的根的偏移。
2. I: i中的R高位替换为1之后的值
3. Rh: R的最高位
4. Roff: mini tree的根在同一层的偏移, Roff是R去掉最高位之后的结果

举一个例子, 假设K=3
| Rh | Roff  | I |
|----|-------|---|
| 1  | 01101 | 11|

```
R = 101101
I = (1)11

x = Rh + Roff * B + I - 1
  = Rh + (R - Rh) * B + I - 1
  = R - Roff + Roff * B
  = R + Roff * (B - 1) + I - 1
```

# 代码

```
const uint32_t K = 3;
const uint32_t B = (1U<<K) - 1;
uint32_t bbt_layout(uint32_t i)
{
   assert(i != 0);
   uint32_t bits = 32 - __builtin_clz(i);
   uint32_t lowbits = bits % K;
   uint32_t R = i >> lowbits;
   uint32_t Rh = 1U<<(bits - lowbits - 1);
   uint32_t Roff = R & ~Rh;
   uint32_t I = i - (R - 1)<<lowbits;
   return Rh + Roff * B + I  - 1;
}
```
