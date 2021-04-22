---
layout: post
title: "filt warning"
---

# step 0: prepare `file.list`
one file per line
```
cat file.list
a/xxx.cpp
a/xxx.h
```

# step 1: make sure build dir is clean
```
rm -rf build_debug_strict
./build.sh debug_strict --init
```

# step 2: generate mybuild.sh
```
grep '.cpp' file.list | xargs -n 1 code.py cmake > mybuild.sh
```

# step 3: add a toplevel makefile
`cat makefile`
```
all:
        build_dir=~/work/master-warning/build_debug_strict sh mybuild.sh | code.py filt_warning file.list
```

# step 4: make and fix warnings
launch make cmd in your editor and fix warnings.
