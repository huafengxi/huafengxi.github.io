---
layout: post
title: "__cax_guard_acquire"
---

# reference
https://libcxxabi.llvm.org/spec.html

# demo程序
```
#include <stdio.h>
int __cxa_guard_acquire(char* guard) { return 1; }
class A
{
public:
  A() { printf("A()\n"); }
  ~A() {}
};

A& getA() {
  static A a;
  return a;
}

int main() {
  getA();
  getA();
  return 0;
}
```
上述代码会连续构造两次A, 如果`__cxa_guard_acquire`返回0, A一次都不会构造。

# __cxa_guard_acquire在初始化完成后还会再被调用吗
通过单测验证，在gcc4.8上__cxa_guard_acquire初始化成功之后就不会在被调用。
但是在gcc5.2上初始化成功之后还会被继续调用，每次获取static成员都会被调用一次。

# 优化的__cxa_guard_acquire
假如某些libstdc++实现的__cax_guard_acquire实现不优，可以自定义一个函数去替换它。
```
inline int __cxa_guard_acquire(char* guard) {
	if (__atomic_load_n(guard, __ATOMIC_ACQUIRE)) return 0;
	if (!__atomic_test_and_set(guard+1, __ATOMIC_SEQ_CST)) return 1;
        while(!__atomic_load_n(guard, __ATOMIC_ACQUIRE))
             ;
        return 0;
}
```
