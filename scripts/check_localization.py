#!/usr/bin/env python3
"""Kiem tra AMCL: in /amcl_pose (+ do bat dinh) va so voi vi tri that cua robot trong Gazebo.

Vi tri that lay tu topic /sim_ground_truth_pose (nav_msgs/Odometry, frame world cua Gazebo).
Robot spawn tai (-2.5, -3.0, yaw 0) trong world, con goc ban do nam tai diem sau undock, nen
sai khac co dinh giua hai he truc la (spawn_x, spawn_y). In ca hai de doi chieu.
"""
import math

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

rclpy.init()
node = rclpy.create_node('check_localization')
box = {}
amcl_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                      reliability=ReliabilityPolicy.RELIABLE)
node.create_subscription(PoseWithCovarianceStamped, 'amcl_pose',
                         lambda m: box.__setitem__('amcl', m), amcl_qos)
node.create_subscription(Odometry, 'sim_ground_truth_pose',
                         lambda m: box.__setitem__('gt', m), 10)
node.create_subscription(Odometry, 'odom', lambda m: box.__setitem__('odom', m), 10)
for _ in range(40):
    rclpy.spin_once(node, timeout_sec=1.0)
    if 'amcl' in box and 'odom' in box:
        break


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


a = box.get('amcl')
if a:
    p = a.pose.pose.position
    c = a.pose.covariance
    print(f'AMCL  : x={p.x:.3f} y={p.y:.3f} yaw={math.degrees(yaw_of(a.pose.pose.orientation)):.1f} deg')
    print(f'        do bat dinh: sigma_x={math.sqrt(c[0]):.3f} m  sigma_y={math.sqrt(c[7]):.3f} m  '
          f'sigma_yaw={math.degrees(math.sqrt(c[35])):.1f} deg')
else:
    print('Chua co /amcl_pose (chua dat initial pose?)')
g = box.get('gt')
if g:
    p = g.pose.pose.position
    print(f'Gazebo: x={p.x:.3f} y={p.y:.3f} yaw={math.degrees(yaw_of(g.pose.pose.orientation)):.1f} deg  (frame world)')
o = box.get('odom')
if o:
    p = o.pose.pose.position
    print(f'Odom  : x={p.x:.3f} y={p.y:.3f}')
node.destroy_node()
rclpy.shutdown()
