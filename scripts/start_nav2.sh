#!/usr/bin/env bash
# Phan 4: chay Nav2 (planner, controller, bt_navigator, behavior, costmap...) tren ban do da luu.
# Phai chay SAU start_localization.sh (AMCL/map_server cung cap map->odom va /map) va sau khi da dat initial pose.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
exec ros2 launch turtlebot4_navigation nav2.launch.py use_sim_time:=true \
  params_file:="$DIR/config/nav2.yaml" "$@"
