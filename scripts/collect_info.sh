#!/usr/bin/env bash
# Thu thap thong tin he thong dang chay (node, topic, TF, tham so) vao logs/06_system_info.log cho bao cao.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
OUT="$DIR/logs/06_system_info.log"
{
echo "### ros2 node list (nav2 + localization)"
ros2 node list 2>/dev/null | grep -E "amcl|map_server|planner|controller|bt_navigator|behavior|costmap|smoother|waypoint|lifecycle|motion_control|diffdrive|rplidar|lidar_bridge|robot_state" | sort
echo; echo "### ros2 topic list -t (chinh)"
ros2 topic list -t 2>/dev/null | grep -E "^/(scan|odom|cmd_vel|map|amcl_pose|initialpose|particle_cloud|tf|tf_static|plan|goal_pose|clock|local_costmap/costmap |global_costmap/costmap |received_global_plan)|navigate_to_pose/_action/status"
echo; echo "### ros2 topic info /scan /odom /cmd_vel"
for t in /scan /odom /cmd_vel; do ros2 topic info $t 2>/dev/null; done
echo; echo "### tan so"
for t in /scan /odom /amcl_pose; do echo -n "$t: "; timeout 8 ros2 topic hz $t --window 10 2>&1 | grep -m1 "average rate"; done
echo; echo "### TF map -> base_link"
timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -m1 -A4 "At time"
echo; echo "### ros2 action list"
ros2 action list 2>/dev/null | grep -E "navigate|compute|follow|spin|backup"
echo; echo "### lifecycle"
for n in map_server amcl planner_server controller_server bt_navigator; do echo -n "$n: "; ros2 lifecycle get /$n 2>&1; done
echo; echo "### Nav2 tham so chinh"
for p in "controller_server FollowPath.plugin" "controller_server FollowPath.max_vel_x" "controller_server FollowPath.max_vel_theta" "controller_server general_goal_checker.xy_goal_tolerance" "planner_server GridBased.plugin" "global_costmap/global_costmap robot_radius" "global_costmap/global_costmap inflation_layer.inflation_radius" "local_costmap/local_costmap inflation_layer.inflation_radius" "amcl robot_model_type" "amcl max_particles" "amcl laser_model_type"; do set -- $p; echo -n "/$1 $2 = "; ros2 param get /$1 $2 2>&1 | head -1; done
} > "$OUT" 2>&1
echo "Da ghi $OUT"
