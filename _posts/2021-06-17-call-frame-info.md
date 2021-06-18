---
layout: post
title: call frame info
---

# ref
https://www.imperialviolet.org/2017/01/18/cfi.html

# glibc setcontext的例子

```
# find . -name setcontext*
    fldenv  (%rcx)
        ldmxcsr oMXCSR(%rdi)


        /* Load the new stack pointer, the preserved registers and
           registers used for passing args.  */
        cfi_def_cfa(%rdi, 0)
        cfi_offset(%rbx,oRBX)
        cfi_offset(%rbp,oRBP)
        cfi_offset(%r12,oR12)
        cfi_offset(%r13,oR13)
        cfi_offset(%r14,oR14)
        cfi_offset(%r15,oR15)
        cfi_offset(%rsp,oRSP)
        cfi_offset(%rip,oRIP)

        movq    oRSP(%rdi), %rsp
        movq    oRBX(%rdi), %rbx
        movq    oRBP(%rdi), %rbp
        movq    oR12(%rdi), %r12
        movq    oR13(%rdi), %r13
        movq    oR14(%rdi), %r14
        movq    oR15(%rdi), %r15
```
