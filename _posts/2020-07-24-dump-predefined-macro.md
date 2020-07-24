---
layout: post
title: dump predefined macro
---

[detecting cpu architecture](https://stackoverflow.com/questions/152016/detecting-cpu-architecture-compile-time)
```
gcc -march=native -dM -E -  </dev/null
```

# test arch
```
#if __x86_64__
#else if __aarch64__
#endif
```
