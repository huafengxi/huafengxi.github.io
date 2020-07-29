---
layout: post
title: sigsegv not logging to dmesg
---

# ref
[stackoverflow](https://unix.stackexchange.com/questions/425302/toggling-visibility-of-segmentation-fault-messsages-in-dmesg)

```
sysctl debug.exception-trace=1  kernel.print-fatal-signals=1
```

另外一点是printk的日志级别设置 [link](https://blog.csdn.net/tonywgx/article/details/17504001)
