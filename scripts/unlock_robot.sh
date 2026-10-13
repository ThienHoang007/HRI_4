#!/usr/bin/env bash
# Mo khoa robot sau khi Gazebo da len: tat cam bien chong lui cua Create 3 va roi tram sac.
# Thieu buoc nay robot se tu dung / quay ve khi di xa tram sac.
source /opt/ros/humble/setup.bash
echo "Cho /motion_control san sang..."
until ros2 param get /motion_control safety_override >/dev/null 2>&1; do sleep 2; done
ros2 param set /motion_control safety_override backup_only
ros2 action send_goal /undock irobot_create_msgs/action/Undock "{}"
