#!/usr/bin/env python3
"""Sinh worlds/maze_small.sdf: san 8x8 m, tuong bien + vai vach ngan + 2 vat can.

Moi vach la (ten, x, y, dai_x, dai_y). Cao 1 m (LiDAR o ~0.3 m nen thay duoc).
"""
import os

T = 0.1  # do day tuong (m)
WALLS = [
    # tuong bien 8x8 m
    ('north', 0, 4, 8.1, T), ('south', 0, -4, 8.1, T),
    ('east', 4, 0, T, 8.1), ('west', -4, 0, T, 8.1),
    # vach doc x=-1.2 tu y=-4 den y=0.5: chia san thanh 2 khu, chua loi di o phia tren
    ('partition_a', -1.2, -1.75, T, 4.5),
    # vach ngang y=1.5 tu x=0.5 den x=4: tao hanh lang phia bac
    ('partition_b', 2.25, 1.5, 3.5, T),
    # hai vat can hop
    ('box_1', 2.0, -2.2, 1.0, 1.0),
    ('box_2', -2.6, 2.4, 0.8, 0.8),
]

LINK = """            <link name='{n}'>
                <pose>{x} {y} 0.5 0 0 0</pose>
                <collision name='{n}_collision'><geometry><box><size>{sx} {sy} 1</size></box></geometry></collision>
                <visual name='{n}_visual'>
                    <geometry><box><size>{sx} {sy} 1</size></box></geometry>
                    <material><ambient>0.1 0.1 0.1 1</ambient><diffuse>0 0.1 0.2 1</diffuse></material>
                </visual>
            </link>
"""

HEAD = """<?xml version="1.0"?>
<!-- Sinh tu gen_world.py. World nho hon maze goc de mo phong nhe hon (CPU render). -->
<sdf version='1.8'>
    <world name='maze_small'>
        <physics name='1ms' type='ignored'>
            <max_step_size>0.003</max_step_size>
            <real_time_factor>1</real_time_factor>
            <real_time_update_rate>1000</real_time_update_rate>
        </physics>
        <plugin name='ignition::gazebo::systems::Physics' filename='ignition-gazebo-physics-system' />
        <plugin name='ignition::gazebo::systems::UserCommands' filename='ignition-gazebo-user-commands-system' />
        <plugin name='ignition::gazebo::systems::SceneBroadcaster' filename='ignition-gazebo-scene-broadcaster-system' />
        <plugin name='ignition::gazebo::systems::Contact' filename='ignition-gazebo-contact-system' />
        <light name='sun' type='directional'>
            <cast_shadows>0</cast_shadows>
            <pose>0 0 10 0 0 0</pose>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
            <direction>-0.5 0.1 -0.9</direction>
        </light>
        <gravity>0 0 -9.8</gravity>
        <scene>
            <ambient>0.4 0.4 0.4 1</ambient>
            <background>0.7 0.7 0.7 1</background>
            <shadows>0</shadows>
        </scene>
        <model name='ground_plane'>
            <static>1</static>
            <link name='link'>
                <collision name='collision'><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></collision>
                <visual name='visual'>
                    <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
                    <material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>
                </visual>
            </link>
        </model>
        <model name='arena'>
            <static>true</static>
"""

tail = "        </model>\n    </world>\n</sdf>\n"
body = ''.join(LINK.format(n=n, x=x, y=y, sx=sx, sy=sy) for n, x, y, sx, sy in WALLS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maze_small.sdf')
with open(out, 'w') as f:
    f.write(HEAD + body + tail)
print('wrote', out)
