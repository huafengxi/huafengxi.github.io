---
layout: post
title: "use google to translate comments"
---

# step1: prepare src file list
```
echo src/a.cpp lib/b.cpp > file.list
```

# step2: extract comment
```
cat `cat file.list` | code.py dump_comment | code.py none_ascii > my.chi.txt
```

# step3: use google to translate txt file
https://translate.google.com/?sl=auto&tl=en&op=docs

# step4: paste chinese and english text to one file
```
paste -d '\n' my.chi.txt my.eng.txt > comp.txt
```
# step5: check and tune the translation result

# step6: import translation result
```
for f in `cat file.list`; do cat $f | code.py upate_comment comp.txt > $f; done
```

# step7: check result
```
git diff
```
