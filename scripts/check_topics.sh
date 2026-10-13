#!/usr/bin/env bash
# Kiem tra nhanh cac topic co ban cua TurtleBot 4 dang chay trong Gazebo.
# Log duoc ghi vao logs/01_topic_check.log de dua vao bao cao.
source /opt/ros/humble/setup.bash
DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR/logs"
OUT="$DIR/logs/01_topic_check.log"

{
  echo '$ ros2 topic list | grep -E "^/(scan|odom|cmd_vel|tf|clock)$"'
  ros2 topic list | grep -E '^/(scan|odom|cmd_vel|tf|clock)$'
  echo
  for t in /scan /odom /cmd_vel; do
    echo "\$ ros2 topic info $t -v"
    ros2 topic info "$t" -v > "$DIR/logs/.info.tmp"
    head -12 "$DIR/logs/.info.tmp"
    echo
  done
  echo '$ ros2 topic hz /scan   (6 s)'
  timeout 6 ros2 topic hz /scan
  echo
  echo '$ ros2 topic hz /odom   (6 s)'
  timeout 6 ros2 topic hz /odom
  echo
  echo '$ ros2 topic echo /odom --once'
  ros2 topic echo /odom --once | head -30
} 2>&1 | tee "$OUT"
