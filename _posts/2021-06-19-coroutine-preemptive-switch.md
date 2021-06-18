---
layout: post
title: coroutine preemptive switch
---

# 参考golang
https://github.com/golang/proposal/blob/master/design/24543-non-cooperative-preemption.md

# 中断执行的方法
使用signal，在signal handler里修改ucontext，从而在sigreturn的时候跳转到调度器逻辑。

# safe point
如果中断在调度器逻辑， 或者调度器和协程切换过程中，signal handler应该立即返回，因为这个点不是我们期望中断的。

# signal handler执行过程中再次收到signal
首先应该避免同意的signal被触发，因此要block自己当前处理的signal(只要不设置SA_NODEFER, 这就是缺省逻辑)

如果收到了其它的signal，其它的signal handler结束后回到当前signal handler，理论上不影响。

# signal handler能否不返回
如果signal handler不返回，直接切换到另一个协程，那么有几个问题:
1. 占用了signal stack
2. 下一个signal无法触发, 除非自己改signal mask。
因此signal handler最好要很快返回，不应该在signal handler里面执行调度逻辑。

# ucontext的问题
协程可以在任意一条指令的地方被打断，因此中断的时候需要把所有寄存器都保存下来。

我们需要解决两个问题：
1. xmm/ymm/zmm寄存器无法从ucontext中获取。rflags是否有效也不确定。
2. setcontext没有恢复rflags，同时还会破坏rax。另外ucontext中的rax是否有效也不确定。
3. ucontext_t无法直接拷贝，引发浮点状态的指针拷贝的时候需要更改。

# reinvent ucontext
鉴于ucontext/setcontext无法直接使用，因此需要自己实现配套的保存逻辑。
