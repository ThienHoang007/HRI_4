#!/usr/bin/env bash
# So sanh du lieu LiDAR tho cua Gazebo voi du lieu qua bridge, va pose that cua robot.
source /opt/ros/humble/setup.bash
DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$DIR/logs"
OUT="$DIR/logs/03_inspect_gz.log"
SCAN=/world/maze/model/turtlebot4/link/rplidar_link/sensor/rplidar/scan

{
  echo '== Gazebo raw scan (tom tat) =='
  timeout 20 ign topic -e -n 1 -t "$SCAN" > "$DIR/logs/.gz_scan.tmp" 2>&1
  grep -E "^(frame|count|angle_min|angle_max|range_min|range_max|vertical_count)" "$DIR/logs/.gz_scan.tmp" | head -10
  echo "so gia tri ranges:  $(grep -c '^ranges:' "$DIR/logs/.gz_scan.tmp")"
  echo "gia tri ranges khac nhau (5 dau):"
  grep '^ranges:' "$DIR/logs/.gz_scan.tmp" | sort | uniq -c | sort -rn | head -5

  echo
  echo '== Pose that cua robot trong Gazebo =='
  timeout 20 ign topic -e -n 1 -t /world/maze/dynamic_pose/info > "$DIR/logs/.gz_pose.tmp" 2>&1
  grep -B2 -A12 'name: "turtlebot4"' "$DIR/logs/.gz_pose.tmp" | head -30

  echo
  echo '== Mo hinh trong world =='
  timeout 20 ign model --list 2>&1 | head -20
} 2>&1 | tee "$OUT"
