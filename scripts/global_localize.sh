#!/usr/bin/env bash
# Dinh vi toan cuc cho AMCL: rai particle khap ban do (/reinitialize_global_localization),
# roi cho robot xoay cham + tien nhe de cac particle sai bi loai dan. Khong can biet truoc vi tri.
source /opt/ros/humble/setup.bash
ros2 service call /reinitialize_global_localization std_srvs/srv/Empty
for i in 1 2 3; do
  timeout 20 ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{angular: {z: 0.3}}" > /dev/null
  timeout 6 ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.08}}" > /dev/null
done
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}" > /dev/null
