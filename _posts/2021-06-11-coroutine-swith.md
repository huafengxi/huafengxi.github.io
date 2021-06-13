---
layout: post
title: coroutine context switch
---

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

# show backtrace
```
define ubt
set $sp=uthread_ctrl_.jc_
set $pc=*((uint64_t*)$sp - 1)
bt
end
