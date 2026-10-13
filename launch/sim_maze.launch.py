"""Phan 1: TurtleBot 4 trong Gazebo (Ignition Fortress), world maze, kem RViz2.

Dung lai launch co san cua turtlebot4_ignition_bringup, chi dat gia tri mac dinh
phu hop voi bai thuc hanh (world maze, model standard, bat RViz2).
"""
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    pkg_bringup = get_package_share_directory('turtlebot4_ignition_bringup')

    args = [
        DeclareLaunchArgument('world', default_value='maze'),
        DeclareLaunchArgument('model', default_value='standard'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
    ]

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_bringup, 'launch', 'turtlebot4_ignition.launch.py'])),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'model': LaunchConfiguration('model'),
            'rviz': LaunchConfiguration('rviz'),
            'x': LaunchConfiguration('x'),
            'y': LaunchConfiguration('y'),
            'yaw': LaunchConfiguration('yaw'),
        }.items())

    return LaunchDescription(args + [sim])
