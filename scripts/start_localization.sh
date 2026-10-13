#!/usr/bin/env bash
# Phan 3: nap ban do da luu (maps/map.yaml) va chay AMCL + map_server (Nav2 localization).
# Chay sau khi: kill_sim.sh -> start_sim.sh -> unlock_robot.sh (robot o lai vi tri sau undock,
# trung voi goc toa do cua ban do vi luc quet SLAM duoc bat ngay sau undock).
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
exec ros2 launch turtlebot4_navigation localization.launch.py use_sim_time:=true \
  map:="$DIR/maps/map.yaml" params:="$DIR/config/localization.yaml" "$@"
