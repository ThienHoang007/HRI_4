#!/usr/bin/env bash
# Liet ke cac luong (thread) ngon CPU nhat cua Gazebo server de tim diem nghen.
PID=$(pgrep -f "^ign gazebo .*maze_small" | head -1)
echo "gazebo server pid=$PID"
top -H -b -n 1 -p "$PID" | sed -n 7,22p
echo
echo "== Tien trinh khac ngon CPU =="
ps -eo pcpu,args --sort=-pcpu | sed -n 2,7p | cut -c1-110
echo
echo "== Bien moi truong LP_NUM_THREADS / LIBGL =="
tr '\0' '\n' < /proc/$PID/environ | grep -E "^(LP_NUM_THREADS|LIBGL_ALWAYS_SOFTWARE|AMENT_PREFIX_PATH)=" | cut -c1-160
