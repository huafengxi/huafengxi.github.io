---
layout: post
title: "section vs segment"
---

# reference
https://stackoverflow.com/questions/14361248/whats-the-difference-of-section-and-segment-in-elf-file-format

section用来给linker使用，segment用来给loader使用。
一个segment可以包含一个或多个section.
# show elf header
```
readelf -l /bin/date
```

# linker script
linker script是用来指导如何把section组成segment。
