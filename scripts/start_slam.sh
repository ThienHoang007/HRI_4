#!/usr/bin/env bash
# Phan 2: chay SLAM Toolbox voi cau hinh config/slam_small.yaml.
#   sync:=false -> node async: bo qua scan khi dang ban, khong de hang doi dong lai
#   (node sync xu ly tung scan nen bi tut lai khi mo phong cham -> ban do tre va nhieu).
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
exec ros2 launch turtlebot4_navigation slam.launch.py use_sim_time:=true sync:=false \
  params:="$DIR/config/slam_small.yaml" "$@"
