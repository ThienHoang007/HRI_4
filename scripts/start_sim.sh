#!/usr/bin/env bash
# Khoi dong mo phong TurtleBot 4 trong world nho (worlds/maze_small.sdf).
#   - LIBGL_ALWAYS_SOFTWARE=1: bat buoc tren may nay (GPU AMD Vega 8 render LiDAR sai).
#   - overlay/turtlebot4_description: ban sao URDF voi LiDAR 10 Hz (goc 62 Hz) va camera 1 Hz
#     (goc 30 Hz) de mo phong chay nhanh hon khi render bang CPU.
# Cach dung:  start_sim.sh [gui:=true|false] [cac tham so launch khac]
DIR="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/humble/setup.bash
export LIBGL_ALWAYS_SOFTWARE=1
# Luu y: Gazebo Transport dung multicast tren card mang. Neu Wi-Fi bi rot giua chung, bridge bao
# "Network is unreachable" va /odom, /scan ngung ve ROS -> can chay lai mo phong khi co mang.
# (Khong dat IGN_IP=127.0.0.1: loopback khong ho tro multicast nen Gazebo khong tim thay world.)
export AMENT_PREFIX_PATH="$DIR/overlay/turtlebot4_description:$DIR/overlay/irobot_create_description:$AMENT_PREFIX_PATH"
exec ros2 launch "$DIR/launch/sim_small.launch.py" "$@"
