#!/usr/bin/env bash
# heartbeat-loop.sh — heartbeat 常驻循环（替代 cron，由 make heartbeat.start 管理）
#
# 行为：启动时不立即执行，先等到下一个北京时间 09:00（本机时区即 Asia/Shanghai），
# 到点执行 assistant/heartbeat.sh，然后睡到次日 09:00，无限循环。
# 日志追加到 run/logs/heartbeat.log（每次启动/唤醒/执行/下次触发时间）。
# SIGTERM/SIGINT 优雅退出（trap）。
set -u

WS=/home/yuanqi.xhf/m
LOG=$WS/run/logs/heartbeat.log
mkdir -p "$WS/run/logs"

CHILD=0

on_term() {
  echo "$(date '+%F %T') [heartbeat-loop] 收到 TERM/INT，优雅退出 (pid $$)" >> "$LOG"
  # 若正在 sleep 或执行 heartbeat.sh，终止子进程
  [ "$CHILD" -ne 0 ] && kill "$CHILD" 2>/dev/null
  exit 0
}
trap on_term TERM INT

# 下一个 09:00 的 epoch（今日未到取今日，已过取明日）
next_fire() {
  local now today9
  now=$(date +%s)
  today9=$(date -d "$(date +%F) 09:00:00" +%s)
  if [ "$now" -lt "$today9" ]; then
    echo "$today9"
  else
    date -d "$(date -d tomorrow +%F) 09:00:00" +%s
  fi
}

echo "$(date '+%F %T') [heartbeat-loop] 启动 (pid $$)，由 make heartbeat.start 管理" >> "$LOG"

while :; do
  target=$(next_fire)
  echo "$(date '+%F %T') [heartbeat-loop] 下次触发: $(date -d "@$target" '+%F %T')" >> "$LOG"

  # 分片 sleep（每段最多 60s），保证 TERM 能被及时处理
  while :; do
    now=$(date +%s)
    [ "$now" -ge "$target" ] && break
    rem=$((target - now))
    [ "$rem" -gt 60 ] && rem=60
    sleep "$rem" &
    CHILD=$!
    wait "$CHILD" 2>/dev/null
    CHILD=0
  done

  echo "$(date '+%F %T') [heartbeat-loop] 到点，执行 assistant/heartbeat.sh" >> "$LOG"
  "$WS/assistant/heartbeat.sh" >> "$LOG" 2>&1 &
  CHILD=$!
  wait "$CHILD" 2>/dev/null
  rc=$?
  CHILD=0
  echo "$(date '+%F %T') [heartbeat-loop] heartbeat.sh 执行完毕 exit=$rc" >> "$LOG"
done
