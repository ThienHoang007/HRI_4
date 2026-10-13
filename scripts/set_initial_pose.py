#!/usr/bin/env python3
"""Dat vi tri ban dau cho AMCL (tuong duong cong cu "2D Pose Estimate" trong RViz2).

Publish geometry_msgs/PoseWithCovarianceStamped len /initialpose trong frame map.
Dung:  set_initial_pose.py [x] [y] [yaw_rad] [sigma_xy_m] [sigma_yaw_rad]   (mac dinh 0 0 0 0.5 0.26)
"""
import math
import sys
import time

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy

args = sys.argv[1:] + ['0', '0', '0', '0.5', '0.26'][len(sys.argv[1:]):]
x, y, yaw, sxy, syaw = (float(v) for v in args[:5])

rclpy.init()
node = rclpy.create_node('set_initial_pose')
node.set_parameters([rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)])
pub = node.create_publisher(PoseWithCovarianceStamped, 'initialpose',
                            QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE))

msg = PoseWithCovarianceStamped()
msg.header.frame_id = 'map'
msg.pose.pose.position.x = x
msg.pose.pose.position.y = y
msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
cov = [0.0] * 36
cov[0] = cov[7] = sxy ** 2      # phuong sai vi tri (mac dinh sigma 0.5 m)
cov[35] = syaw ** 2             # phuong sai huong (mac dinh sigma 0.26 rad ~ 15 do)
msg.pose.covariance = cov

# cho AMCL san sang nhan, roi gui vai lan (sim cham nen de bi roi)
for _ in range(20):
    rclpy.spin_once(node, timeout_sec=0.2)
    if pub.get_subscription_count() > 0:
        break
for _ in range(3):
    msg.header.stamp = node.get_clock().now().to_msg()
    pub.publish(msg)
    rclpy.spin_once(node, timeout_sec=0.5)
    time.sleep(0.5)
print(f'Da dat initial pose: x={x} y={y} yaw={yaw} rad (frame map)')
node.destroy_node()
rclpy.shutdown()
