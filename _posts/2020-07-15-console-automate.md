---
layout: post
title: console automate
---

# pexpect
```
import pexpect
p = pexpect.spawn(cmd)
while p.expect([pexpect.eof, '\(y/n\)']):
    print p.before
    p.send('y')
print p.before
p.interact()
```

# editor
如果编辑文件有缺省内容
```
export EDITOR=true
```
