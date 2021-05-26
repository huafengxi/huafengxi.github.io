---
layout: post
title: git list missing patch
---

Is there some critical bugfix I forget to patch to the release branch?
You can check by following steps.

# list commit since fork
```
git log origin/2_2_x_release..origin/master --author=obdev --grep='Author : 元启' > a2b.log
git log origin/master..origin/2_2_x_release --author=obdev --grep='Author : 元启' > b2a.log
```

# filter the manually patching after fork
download git.py from [here](http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/git.py)
```
# for each commit in a2b.log, if the commit's title appear in b2a.log, then filter it.
cat a2b.log | git.py filt 'Title: .+\n' b2a.log
```

# simple shell script wrapper
```
b1=origin/2_2_3_release
b2=origin/master
author=元启
git log $b1..$b2 --author=obdev --grep="Author : $author" > a2b.log
git log $b2..$b1 --author=obdev --grep="Author : $author" > b2a.log
cat a2b.log | git.py filt 'Title: .+\n' b2a.log
```

# gen html link
```
# generate one diff for each commit, named by its hashcode
cat xxx.log | git.py html
```
