---
layout: post
title: why can not rm file
---

很可能是通过"高级的attr"设置文件或目录保护了。 参考 https://www.sklinux.com/posts/devops/linux%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E9%AB%98%E7%BA%A7%E6%9D%83%E9%99%90%E5%B1%9E%E6%80%A7/

查看attr
```
lsattr xxx
```

清除attr
```
sudo chattr -a -e -R xxx
```
