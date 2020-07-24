---
layout: post
title: full specializations not allowed in class scope
---

# reference
full specializations not allowed in class scope, even though partial are	
[cppreference](https://en.cppreference.com/w/cpp/language/template_specialization)

注意，在足够新的编译器上，这个问题是被修复的。

# 错误例子
```
class A {
template <int i>
struct B{};

template<>
struct B<0> {};
};
```
报错
```
a.cpp:5:10: error: explicit specialization in non-namespace scope ‘class A’
 template<>
```

# 正确的例子
```
class A {
template <int i, typename IGNORE=void>
struct B{};

template<typename IGNORE>
struct B<0, IGNORE> {};
};
```

# 或者把B放到class外面
只是这种方法不一定满足需求。
