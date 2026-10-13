#!/usr/bin/env python3
"""In thong ke ban do /map (o da biet, o tuong) va vi tri robot de theo doi tien do quet."""
import rclpy
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

rclpy.init()
node = rclpy.create_node('map_stats')
box = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                 reliability=ReliabilityPolicy.RELIABLE)
node.create_subscription(OccupancyGrid, 'map', lambda m: box.__setitem__('map', m), qos)
node.create_subscription(Odometry, 'odom', lambda m: box.__setitem__('odom', m), 10)
for _ in range(30):
    rclpy.spin_once(node, timeout_sec=1.0)
    if len(box) == 2:
        break
m = box.get('map')
if m:
    d = m.data
    free = sum(1 for v in d if v == 0)
    occ = sum(1 for v in d if v > 50)
    res = m.info.resolution
    print(f'map {m.info.width}x{m.info.height} res={res} free={free * res * res:.1f} m2 '
          f'occupied_cells={occ} origin=({m.info.origin.position.x:.1f},{m.info.origin.position.y:.1f})')
o = box.get('odom')
if o:
    p = o.pose.pose.position
    print(f'odom x={p.x:.2f} y={p.y:.2f}')
node.destroy_node()
rclpy.shutdown()
