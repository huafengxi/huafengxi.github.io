---
layout: post
title: "privacy backup to github"
---

# 敏感数据的备份
github允许创建private仓库，如果想进一步提高安全性，可以checkin gpg加密后的文件，或者用git-crypt插件实现commit自动加密。

git-crypt checkout下来之后会自动解密，因此对特别私密的文件，比如密码本，建议手工用gpg加密，只有查看的时候才临时解密。

# 密码本
尽量不要多个账号共享密码，但密码多了很容易忘记。
解决方法是用一个文本文件记录各个密码，可以用两种方法保证安全：
1. 文本文件不要直接记录密码，建议记录hint。
2. 文本文件可以用GPG加密。

# ssh私钥的备份
`id_rsa.pub`可以公开，`id_rsa`可以设置pass phrase，然后可以用gpg二次加密，这样安全性足够，
pass phrase的hint可以放到密码本里。

# gpg key的备份
gpg key设置pass phrase + 对称加密, 然后可以放到github仓库。
对称加密的密码和pass phrase的hint不能放到密码本，否则一旦忘记密码就死循环了， 只能放到明文文件里。

因此这一步的安全性是通过github密码和明文文件的hint来保证的，github密码的hint只能用github之外的方式记录下来。

# github密码
密码hint可以用只有你自己知道的方式写到公开的博客里。

# 换电脑的恢复流程
1. 搞定github密码，登录github。
2. 手工查看git仓库里的恢复指引，恢复指引第一步是要下载gpg key，并导入到本机。
3. 有了gpg key，可以下载ssh key，解压ssh key之后可以git clone仓库。
4. git clone后，设置好git-crypt, 就可以解密私密文件。
5. 其它网站的登录密码，可以用gpg解密密码本。

# github挂掉怎么办？
正常来说你的本地也会有clone，因此github和本地同时丢数据才会真的有问题。
