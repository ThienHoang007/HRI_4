#!/usr/bin/env python3
"""Gui lan luot nhieu goal NavigateToPose (tuong duong cong cu "Nav2 Goal" trong RViz2) va ghi log.

Voi moi goal: in trang thai, thoi gian, quang duong, khoang cach nho nhat toi vat can (tu /scan),
sai so toi dich (tu /amcl_pose). Quy dao luu o logs/nav_trajectory_<ngay>_<gio>.csv (cot: goal, t, x, y, yaw, min_range).
Dung:  send_goals.py x1,y1[,yaw] x2,y2[,yaw] ...      (toa do trong frame map, yaw radian)
"""
import csv
import math
import os
import sys
import time

import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from action_msgs.msg import GoalStatus

LOGS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
goals = []
for a in sys.argv[1:]:
    v = [float(t) for t in a.split(',')]
    goals.append((v[0], v[1], v[2] if len(v) > 2 else 0.0))

rclpy.init()
node = rclpy.create_node('send_goals')
node.set_parameters([rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)])
st = {'pose': None, 'min': None}


def on_amcl(m):
    p = m.pose.pose
    st['pose'] = (p.position.x, p.position.y,
                  math.atan2(2 * (p.orientation.w * p.orientation.z), 1 - 2 * p.orientation.z ** 2))


def on_scan(m):
    r = [v for v in m.ranges if math.isfinite(v) and v > m.range_min]
    st['min'] = min(r) if r else None


node.create_subscription(PoseWithCovarianceStamped, 'amcl_pose', on_amcl,
                         QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                    reliability=ReliabilityPolicy.RELIABLE))
node.create_subscription(LaserScan, 'scan', on_scan, qos_profile_sensor_data)
client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
print('Cho action server navigate_to_pose...')
client.wait_for_server()

os.makedirs(LOGS, exist_ok=True)
csv_path = os.path.join(LOGS, time.strftime('nav_trajectory_%Y%m%d_%H%M%S.csv'))   # moi lan chay mot file, khong ghi de
f = open(csv_path, 'w', newline='')
w = csv.writer(f)
w.writerow(['goal', 't', 'x', 'y', 'yaw', 'min_range'])
overall_min = 9.9
for i, (gx, gy, gyaw) in enumerate(goals, 1):
    msg = NavigateToPose.Goal()
    msg.pose = PoseStamped()
    msg.pose.header.frame_id = 'map'
    msg.pose.pose.position.x, msg.pose.pose.position.y = gx, gy
    msg.pose.pose.orientation.z, msg.pose.pose.orientation.w = math.sin(gyaw / 2), math.cos(gyaw / 2)
    print(f'\n=== Goal {i}: x={gx} y={gy} yaw={gyaw:.2f} ===')
    fut = client.send_goal_async(msg)
    rclpy.spin_until_future_complete(node, fut)
    handle = fut.result()
    if not handle.accepted:
        print('Goal bi tu choi')
        continue
    res = handle.get_result_async()
    t0, last, dist, gmin = time.time(), None, 0.0, 9.9
    while not res.done():
        rclpy.spin_once(node, timeout_sec=0.2)
        if st['pose']:
            x, y, yaw = st['pose']
            if last:
                dist += math.hypot(x - last[0], y - last[1])
            last = (x, y)
            if st['min'] is not None:
                gmin = min(gmin, st['min'])
            w.writerow([i, f'{time.time() - t0:.1f}', f'{x:.3f}', f'{y:.3f}', f'{yaw:.3f}',
                        f'{st["min"]:.3f}' if st['min'] is not None else ''])
        if time.time() - t0 > 600:
            print('Qua 600 s, huy goal')
            handle.cancel_goal_async()
            break
    status = res.result().status if res.done() else -1
    name = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED', GoalStatus.STATUS_ABORTED: 'ABORTED',
            GoalStatus.STATUS_CANCELED: 'CANCELED'}.get(status, str(status))
    err = math.hypot(st['pose'][0] - gx, st['pose'][1] - gy) if st['pose'] else float('nan')
    overall_min = min(overall_min, gmin)
    print(f'Ket qua: {name} | {time.time() - t0:.0f} s (thoi gian thuc) | quang duong {dist:.2f} m | '
          f'sai so toi dich {err:.2f} m | khoang cach nho nhat toi vat can {gmin:.2f} m')
    time.sleep(2)
f.close()
print(f'\nKhoang cach nho nhat toi vat can trong ca hanh trinh: {overall_min:.2f} m '
      f'(robot ban kinh 0.175 m; < 0.2 m nghia la sat/cham tuong)')
node.destroy_node()
rclpy.shutdown()
