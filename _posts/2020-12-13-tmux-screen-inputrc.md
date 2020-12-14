---
layout: post
title: "tmux screen inputrc'
---

# tmux.conf
```
# set -g utf8
# set-window-option -g utf8 on
# make tmux display things in 256 colors
set -g default-terminal "xterm-256color"
#set -g default-terminal "screen-256color"

# set scrollback history to 10000 (10k)
set -g history-limit 10000

unbind C-b
set -g prefix `
bind ` send-prefix

# reload ~/.tmux.conf using PREFIX r
bind r source-file ~/.tmux.conf

set-window-option -g mode-keys vi

# # default statusbar colors
set-option -g status-fg black
set-option -g status-bg blue
set-option -g status-attr default

# # default window title colors
set-window-option -g window-status-fg black
set-window-option -g window-status-bg default
set-window-option -g window-status-attr dim

# # active window title colors
set-window-option -g window-status-current-fg white
set-window-option -g window-status-current-bg red
set-window-option -g window-status-current-attr bright


# # command/message line colors
set-option -g message-fg white
set-option -g message-bg black
set-option -g message-attr bright

# # Refresh the status bar every 30 seconds.
set-option -g status-interval 30

# # The status bar itself.
set -g status-justify left
set -g status-left-length 40
set -g status-left ""
set -g status-right "%R"

set-option -g display-time 1000
```

# .screenrc
```
bind r source-file ~/.tmux.conf

set-window-option -g mode-keys vi

# # default statusbar colors
set-option -g status-fg black
set-option -g status-bg blue
set-option -g status-attr default

# # default window title colors
set-window-option -g window-status-fg black
set-window-option -g window-status-bg default
set-window-option -g window-status-attr dim

# # active window title colors
set-window-option -g window-status-current-fg white
set-window-option -g window-status-current-bg red
set-window-option -g window-status-current-attr bright


# # command/message line colors
set-option -g message-fg white
set-option -g message-bg black
set-option -g message-attr bright

# # Refresh the status bar every 30 seconds.
set-option -g status-interval 30

# # The status bar itself.
set -g status-justify left
set -g status-left-length 40
set -g status-left ""
set -g status-right "%R"

set-option -g display-time 1000
yuanqi.xhf@obvos-dev-b2 ~$ cat .screenrc
escape ``

# hard status and tabs for windows
hardstatus on
hardstatus alwayslastline
hardstatus string "%{.bW}%-w%{.rW}%n %t%{-}%+w %=%{..G} %H %{..Y} %m/%d %c"
defmonitor on
activity 'Activity in window %'

#hardstatus lastline "%c %t %n %w"
#startup_message off
#vbell off
#defscrollback 512

#caption always “%{=u kC} %= %-w%L>%{=b G}[:%n %t:]%{-}%52<%+w %L=”

#deflogin off
# default starting dir is ~
#chdir

# create default screens
screen -fn -t bash -L 0

# switch to window 0
select 0
```

# .inputrc
```
# set editing-mode vi
# set keymap vi
set show-all-if-ambiguous on
"\C-p": history-search-backward
"\C-n": history-search-forward
```
