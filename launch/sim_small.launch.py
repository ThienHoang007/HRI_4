"""TurtleBot 4 trong world nho (worlds/maze_small.sdf, san 8x8 m) de mo phong nhe hon.

Launch goc turtlebot4_ignition.launch.py chi nap world trong thu muc cua package nen khong
dung duoc world cua repo. File nay lam lai cac buoc do:
  1. dat IGN_GAZEBO_RESOURCE_PATH / IGN_GUI_PLUGIN_PATH
  2. chay Ignition Gazebo voi world (tuyet doi) cua repo, tuy chon khong mo GUI (gui:=false)
  3. cau noi /clock
  4. spawn robot + dock + bridge + cac node Create 3 / TurtleBot 4 (turtlebot4_spawn.launch.py)

Tham so: gui (true|false), rviz (true|false), x, y, yaw, model.
"""
import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            OpaqueFunction, SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

WORLD_NAME = 'maze_small'
WORLD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'worlds', WORLD_NAME + '.sdf')


def start_gazebo(context, *args, **kwargs):
    pkg_bringup = get_package_share_directory('turtlebot4_ignition_bringup')
    pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')
    model = LaunchConfiguration('model').perform(context)
    gui = LaunchConfiguration('gui').perform(context) == 'true'

    ign_args = f'{WORLD_FILE} -r -v 2'
    if gui:
        gui_config = os.path.join(pkg_bringup, 'gui', model, 'gui.config')
        ign_args += f' --gui-config {gui_config}'
    else:
        ign_args += ' -s'  # chi chay server, khong ve cua so (tiet kiem CPU)

    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py')),
        launch_arguments=[('ign_args', ign_args)])]


def generate_launch_description():
    pkg_bringup = get_package_share_directory('turtlebot4_ignition_bringup')
    pkg_tb4_desc = get_package_share_directory('turtlebot4_description')
    pkg_create_desc = get_package_share_directory('irobot_create_description')
    pkg_create_ign = get_package_share_directory('irobot_create_ignition_bringup')
    pkg_gui_plugins = get_package_share_directory('turtlebot4_ignition_gui_plugins')
    pkg_create_plugins = get_package_share_directory('irobot_create_ignition_plugins')

    args = [
        DeclareLaunchArgument('gui', default_value='false',
                              description='true: mo cua so Gazebo; false: chi chay server'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('model', default_value='standard',
                              choices=['standard', 'lite']),
        DeclareLaunchArgument('x', default_value='-2.5'),
        DeclareLaunchArgument('y', default_value='-3.0'),
        DeclareLaunchArgument('z', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        # Ten world phai trung voi <world name=...> trong SDF; bridge dung de ghep ten topic.
        DeclareLaunchArgument('world', default_value=WORLD_NAME),
    ]

    resource_path = SetEnvironmentVariable(
        'IGN_GAZEBO_RESOURCE_PATH',
        ':'.join([
            os.path.join(pkg_bringup, 'worlds'),
            os.path.join(pkg_create_ign, 'worlds'),
            str(Path(pkg_tb4_desc).parent.resolve()),
            str(Path(pkg_create_desc).parent.resolve()),
        ]))
    gui_plugin_path = SetEnvironmentVariable(
        'IGN_GUI_PLUGIN_PATH',
        ':'.join([os.path.join(pkg_gui_plugins, 'lib'),
                  os.path.join(pkg_create_plugins, 'lib')]))

    clock_bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                        name='clock_bridge', output='screen',
                        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'])

    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_bringup, 'launch', 'turtlebot4_spawn.launch.py'])),
        launch_arguments={
            'rviz': LaunchConfiguration('rviz'),
            'model': LaunchConfiguration('model'),
            'x': LaunchConfiguration('x'),
            'y': LaunchConfiguration('y'),
            'z': LaunchConfiguration('z'),
            'yaw': LaunchConfiguration('yaw'),
        }.items())

    return LaunchDescription(args + [
        resource_path, gui_plugin_path, OpaqueFunction(function=start_gazebo),
        clock_bridge, spawn])
