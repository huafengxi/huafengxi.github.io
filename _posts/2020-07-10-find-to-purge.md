---
layout: post
title: "find to purge"
---

# reference
`man find`

# example
```
find xxx -cmin +60 --exec rm '{}' \; # purge old file (not modified within 60min)
```
