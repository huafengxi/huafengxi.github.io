---
layout: post
title: git list missing patch
---

Is there some critical bugfix I forget to patch to the release branch?
You can check by following steps.

download git.py from [here](http://051915.oss-cn-hangzhou-zmf.aliyuncs.com/git.py)

# list commit since fork
```
git log origin/2_2_x_release..origin/master --author=obdev --grep='Author : 元启' > a2b.log
git log origin/master..origin/2_2_x_release --author=obdev --grep='Author : 元启' > b2a.log
```

# filter the manually patching after fork
```
# for each commit in a2b.log, if the commit's title appear in b2a.log, then filter it.
cat a2b.log | git.py filt 'Title: .+\n' b2a.log
```

# process the commit hashcode to html link
```
# generate one diff for each commit, named by its hashcode
cat xxx.log | git.py html
```

# wrapped in ob-diff command
```
git.py ob_diff origin/2_2_x_release..origin/master 元启
```
