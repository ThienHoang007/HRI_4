#!/usr/bin/env python3
"""In tom tat 1 ban tin /scan va vi tri /odom de chan doan."""
import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

rclpy.init()
node = rclpy.create_node('inspect_scan')
box = {}
node.create_subscription(LaserScan, 'scan', lambda m: box.setdefault('scan', m),
                         qos_profile_sensor_data)
node.create_subscription(Odometry, 'odom', lambda m: box.setdefault('odom', m), 10)
while rclpy.ok() and len(box) < 2:
    rclpy.spin_once(node, timeout_sec=1.0)

s = box['scan']
n = len(s.ranges)
print(f'n={n} angle_min={math.degrees(s.angle_min):.0f} angle_max={math.degrees(s.angle_max):.0f} '
      f'range_min={s.range_min} range_max={s.range_max}')
for deg in range(-180, 180, 30):
    i = int(round((math.radians(deg) - s.angle_min) / s.angle_increment)) % n
    print(f'  {deg:5d} deg -> {s.ranges[i]:.2f} m')
p = box['odom'].pose.pose.position
print(f'odom x={p.x:.2f} y={p.y:.2f}')
node.destroy_node()
rclpy.shutdown()
