#!/usr/bin/env bash
# Lai robot bang ban phim voi toc do khoi dau thap (mac dinh cua teleop la 0.5 m/s, 1.0 rad/s).
# Dung:  teleop_slow.sh [toc_do_thang m/s] [toc_do_quay rad/s]
# Phim: i tien | , lui | j quay trai | l quay phai | k dung | z/x giam/tang ca hai toc do 10%
# (khong dung q/w/e: chung tang toc do va rat de bi chay mat kiem soat)
SPEED="${1:-0.10}"
TURN="${2:-0.35}"
source /opt/ros/humble/setup.bash
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:="$SPEED" -p turn:="$TURN"
