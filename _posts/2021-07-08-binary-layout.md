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

## code
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

# bbt search
先考虑一个更简单的模型, 每个block放`1<<K`个key，每个key一个子树。这个模型类似于skip list。

定义:
1. L: 表示当前level的起点(每个block当作2的K次方来算)
2. Loff: 表示当前level内的偏移(每个block当作2的K次方来算)
3. I: block内部二叉树下标，从1开始算。

递推规则
1. L的递推规则: `L = (L + 1)<<K`
2. Loff的递推规则: `Loff = Loff<<K`

`<L,Loff,I>`可以之间相加, 这个值实际就是skip list模型序列化的下标
1. 因为L和Loff的递推规则都是类似的，所以可以直接相加
2. 每个block的size都是2的K次方对齐的，所以mini tree内部偏移I可以加到L + Loff上，它们占据不同的二进制位。


用c表示skip list模型迭代的下标
```
uint32_t locate(uint32_t c)
{
   return c - (c>>K) - 1;
}
```


```
uint32_t left_child(uint32_t c)
{
   uint32_t I = c & B;
   c += I;
   if ((I >> (K - 1)) == 0) {
     return c;
   } else {
     return (c<<K) + 1;
   }
}
```
