---
layout: post
title: pthread-mutex
---

# 代码位置
glibc代码目录
```
find . -name 'pthread_mutex_lock*'
find . -name 'pthreadtypes.h'
```

# mutex type
常用的有4种, man pthread_mutex_lock
```
  PTHREAD_MUTEX_TIMED_NP,
  PTHREAD_MUTEX_RECURSIVE_NP,
  PTHREAD_MUTEX_ERRORCHECK_NP,
  PTHREAD_MUTEX_ADAPTIVE_NP
```

# mutex定义
```
typedef union
{
  struct __pthread_mutex_s
  {
    int __lock;
    unsigned int __count;
    int __owner;
#ifdef __x86_64__
    unsigned int __nusers;
#endif
    /* KIND must stay at this position in the structure to maintain
       binary compatibility.  */
    int __kind;
#ifdef __x86_64__
    int __spins;
    __pthread_list_t __list;
# define __PTHREAD_MUTEX_HAVE_PREV      1
#else
    unsigned int __nusers;
    __extension__ union
    {
      int __spins;
      __pthread_slist_t __list;
    };
#endif
  } __data;
  char __size[__SIZEOF_PTHREAD_MUTEX_T];
  long int __align;
} pthread_mutex_t;
```
这几个变量中：
1. kind表示锁的种类
2. lock就是原子操作和futex的变量: 0表示没锁，2表示加锁
3. count和owner是为了支持递归锁
4. spin是为了支持PTHREAD_MUTEX_ADAPTIVE_NP, 用于估计spin次数的。

不能一眼看出用途的是nusers和list这两个变量

首先是nusers变量，它和count看起来差不多，差别在于:
1. count在递归锁的情况下会递增, 并且多次递归加锁，nusers只加一次。
2. nusers是加锁成功递增: 递归锁只有第一次递增，后续不递增；非递归锁加锁成功也递增。还有一个情况是pthread cond wait的时候解锁，但是不改nusers.
目前看来nusers只是debug功能，唯一用于判断的地方是mutex_destroy.


然后是list变量，目前看来主要是为了支持robost futex的。[kernel-doc](https://www.kernel.org/doc/html/latest/locking/robust-futex-ABI.html)

