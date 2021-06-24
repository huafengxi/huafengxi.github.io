---
layout: post
title: "fix mismatch tag compiling warnings
---

# step 0: collect mismatch-tag class/struct list
one file per line
```
cat build.log |code.py filt_warning file.list  |grep mismatch | awk -F "'" '{print $2}' |sort |uniq > mismatch-tag.list
```

# step 1: fix mismatch-tag
```
for f in `cat mismatch-tag.list`; do code.py fix_class_tag $f deps src; done
```
