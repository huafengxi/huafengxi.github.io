---
layout: post
title: coroutine context switch
---

# how many registers?
ttps://blog.yossarian.net/2020/11/30/How-many-registers-does-an-x86-64-cpu-have

# x86 calling convention
https://en.wikipedia.org/wiki/X86_calling_conventions
```
The first six integer or pointer arguments are passed in registers RDI, RSI, RDX, RCX, R8, R9.

If the callee wishes to use registers RBX, RSP, RBP, and R12–R15, it must restore their original values before returning control to the caller. All other registers must be saved by the caller if it wishes to preserve their values.
```

# why swapcontext is slow
https://rethinkdb.com/blog/making-coroutines-fast/
```
You might spot a few unnecessary things here:

1. Argument registers (RDI, RDX, RCX, R8, R9 and RSI) are saved and restored even though the calling convention doesn’t guantee that they’re saved and restored
2. x87 and SSE state is saved and restored, even though we’re not doing anything with floats or SIMD where register contents need to be preserved across function calls
3. The signal mask is saved and restored with the system call sigprocm
```

# example
https://graphitemaster.github.io/fibers/
```
.type get_context, @function
.global get_context
get_context:
  # Save the return address and stack pointer.
  movq (%rsp), %r8
  movq %r8, 8*0(%rdi) // RIP
  leaq 8(%rsp), %r8
  movq %r8, 8*1(%rdi) // RSP

  # Save preserved registers.
  movq %rbx, 8*2(%rdi)
  movq %rbp, 8*3(%rdi)
  movq %r12, 8*4(%rdi)
  movq %r13, 8*5(%rdi)
  movq %r14, 8*6(%rdi)
  movq %r15, 8*7(%rdi)

  # Return.
  xorl %eax, %eax
  ret
```

# fastest switching
https://en.wikipedia.org/wiki/Coroutine#Implementations_for_C
```
may achieve the same result via a small block of inline assembly which swaps merely the stack pointer and program counter, and clobbers all other registers. 
```

# inline asm最简单的实现
```
#define jc_func __attribute__((noipa, optimize(2)))
jc_func void* jc_make(jc_t* s)
{
  void* ret = 0;
  __asm__ volatile (
      "leaq 1f(%%rip), %%rbx\n\t"
      "movq %%rbx, -8(%%rsp)\n\t"
      "movq %%rsp, (%[s])\n\t"
      "xorq %[ret], %[ret]\n\t"
      "1:\n\t"
      :[ret]"=r"(ret)
      :[s]"r"(s)
      :"memory", "rbx", "rbp", "r12", "r13", "r14", "r15");
  return ret;
}

jc_func void* jc_switch(jc_t t, jc_t* s, void* x)
{
  void* ret = 0;
  __asm__ volatile (
      "leaq 1f(%%rip), %%rbx\n\t"
      "movq %%rbx, -8(%%rsp)\n\t"
      "movq %%rsp, (%[s])\n\t"
      "movq %[t], %%rsp\n\t"
      "movq %[x], %[ret]\n\t"
      "jmpq *-8(%[t])\n\t"
      "1:\n\t"
      :[ret]"=r"(ret)
      :[s]"r"(s), [t]"r"(t), [x]"r"(x)
      :"memory", "rbx", "rbp", "r12", "r13", "r14", "r15");
  return ret;
}
```

# show backtrace
```
define ubt
set $sp=uthread_ctrl_.jc_
set $pc=*((uint64_t*)$sp - 1)
bt
end

# inline asm的优化问题
最保险的是禁止inline，但同时要禁止ipa，并且为了代码干净，需要保证O2优化。
```
__attribute__((noipa, noline, optimize(2))
```

如果想inline，一定要在setjmp的时候把所有寄存器（包括caller preserved寄存器都设置为clobber)
具体可以参考libdill/libdill.h

# redzone的影响
如果setjmp被inline了，那么注意一定不能使用redzone的栈空间，最清晰的做法就是不要用任何栈空间。

如果非要用stack保存context，那么有两种做法:
1. 禁止setjmp inline。
2. 避开redzone.
