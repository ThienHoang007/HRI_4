#!/usr/bin/env bash
# Phan 2: luu ban do dang co tren topic /map thanh maps/map.yaml + maps/map.pgm
# (dung nav2_map_server map_saver_cli, do SLAM Toolbox dang publish /map).
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
mkdir -p "$DIR/maps"
python3 "$DIR/scripts/map_stats.py"
ros2 run nav2_map_server map_saver_cli -f "$DIR/maps/map" --ros-args -p save_map_timeout:=20.0 -p free_thresh_default:=0.25 -p occupied_thresh_default:=0.65
echo
ls -la "$DIR/maps"
cat "$DIR/maps/map.yaml"
