#!/usr/bin/env bash
# Chan doan vi sao robot khong di chuyen / tu quay ve khi teleop.
source /opt/ros/humble/setup.bash
DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR/logs"
OUT="$DIR/logs/02_diagnose_motion.log"

run() {
  echo
  echo "\$ $*"
  timeout 8 "$@" 2>&1 | head -40
}

{
  echo "== Bo nho =="
  free -m
  echo
  echo "== Process Gazebo / RViz2 con song? =="
  pgrep -a -f "ign gazebo|rviz2" | cut -c1-120

  echo
  echo "== Toc do mo phong: so sanh /clock voi dong ho that =="
  W1=$(date +%s)
  S1=$(timeout 6 ros2 topic echo /clock --once 2>/dev/null | grep -m1 "sec:" | awk '{print $2}')
  sleep 10
  W2=$(date +%s)
  S2=$(timeout 6 ros2 topic echo /clock --once 2>/dev/null | grep -m1 "sec:" | awk '{print $2}')
  echo "wall: $W1 -> $W2 ; sim: $S1 -> $S2"
  echo "real-time factor ~ $(( (S2 - S1) * 100 / (W2 - W1) )) %"

  run ros2 topic echo /dock_status --once
  run ros2 topic echo /hazard_detection --once
  run ros2 topic echo /cmd_vel --once
  run ros2 topic echo /odom --once --field pose.pose.position
  run ros2 param get /motion_control safety_override
  run ros2 action list
} 2>&1 | tee "$OUT"
