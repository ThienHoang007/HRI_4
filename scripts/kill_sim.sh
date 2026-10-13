#!/usr/bin/env bash
# Dung toan bo tien trinh mo phong TurtleBot 4 (Gazebo, bridge, node Create 3, SLAM, Nav2, RViz2).
# Can chay truoc khi khoi dong lai, neu khong cac node cu se bi trung voi node moi.
# Khong dung teleop_twist_keyboard (de ban tu Ctrl-C).
for p in "ign gazebo" "ros_gz_bridge" "irobot_create" "turtlebot4" "robot_state_publisher" \
         "static_transform_publisher" "joint_state_publisher" "rviz2" "slam_toolbox" "nav2" "map_server" "amcl" \
         "controller_server" "planner_server" "bt_navigator" "behavior_server" "lifecycle_manager" \
         "velocity_smoother" "waypoint_follower" "ros2 launch" "ros2-daemon" "wall_follow_explorer"; do
  pkill -f "$p"
done
sleep 3
pkill -9 -f "ign gazebo"; pkill -9 -f "ros_gz_bridge"; pkill -9 -f "irobot_create"
source /opt/ros/humble/setup.bash
ros2 daemon stop >/dev/null 2>&1
echo "Con lai (mong doi khong co):"
pgrep -af "ign gazebo|ros_gz|irobot_create|turtlebot4|rviz2|slam_toolbox|nav2" | cut -c1-100
echo "Da don xong."
