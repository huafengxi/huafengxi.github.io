---
layout: post
title: git list missing patch
---

Is there some critical bugfix I forget to patch to the release branch?
You can check by following steps.

# step 1: list commit since fork
```
git log origin/2_2_x_release..origin/master --author=obdev --grep='Author : 元启' > a2b.log
git log origin/master..origin/2_2_x_release --author=obdev --grep='Author : 元启' > b2a.log
```

# step 2: filter the manually patching after fork
download git.py from [here](http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/git.py)
```
# for each commit in a2b.log, if the commit's title appear in b2a.log, then filter it.
cat a2b.log | git.py extract_description |git.py filt a2b.log
```

# In one step: define helper shell function
```
function git_diff() { git log $1..$2 --author=obdev --grep="Author : $3" | git.py extract_description | git.py filt <(git log $2..$1); }
git_diff origin/2_2_x_release origin/master 元启
```
