# TurtleBot 4 – SLAM Toolbox, AMCL và Nav2 trong Gazebo (ROS 2 Humble)

Bài thực hành 04: chạy TurtleBot 4 trong Gazebo (Ignition Fortress), dựng bản đồ bằng SLAM Toolbox,
định vị bằng AMCL trên bản đồ đã lưu và điều hướng tự động bằng Nav2.

- Video demo: `[LINK-VIDEO-GOOGLE-DRIVE]`
- Báo cáo: `report/report.pdf` (biên dịch từ `report/report.tex`)

## Cài đặt (Ubuntu 22.04)

```bash
sudo apt install ros-humble-desktop ros-humble-turtlebot4-simulator ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-navigation ros-humble-nav2-bringup ros-humble-slam-toolbox \
  ros-humble-teleop-twist-keyboard
git clone https://github.com/[GITHUB-USER]/[TEN-REPO].git
cd [TEN-REPO]          # thu muc chua launch/, scripts/, maps/ ...
chmod +x scripts/*.sh scripts/*.py
```

Các script dùng thêm `python3-numpy` và `python3-pil` (Pillow) cho `clean_map.py`, `find_pose.py`, `make_figures.py`.

## Lưu ý quan trọng khi chạy

- Mọi script đã `source /opt/ros/humble/setup.bash`. Mỗi lệnh dưới đây chạy trong **một terminal riêng**.
- `start_sim.sh` đặt `LIBGL_ALWAYS_SOFTWARE=1`: máy dùng GPU AMD Vega 8 khiến LiDAR của Gazebo trả về hằng số 0.164 m. Máy khác có thể không cần.
- World `worlds/maze_small.sdf` (8×8 m) là world tự tạo, nhỏ hơn `maze` gốc để mô phỏng nhẹ hơn.
  `overlay/` chứa bản sao URDF đã giảm tần số cảm biến (LiDAR 10 Hz, camera 1 Hz) và được đặt trước trong `AMENT_PREFIX_PATH`.
- Robot Create 3 phải được "mở khóa" (`unlock_robot.sh`) sau khi Gazebo đã lên hẳn, nếu không `/undock` bị rejected (chạy lại là được).
- Gazebo Transport dùng multicast: nếu Wi-Fi rớt, `/odom` và `/scan` ngừng; hãy chạy lại mô phỏng.
- Trước mỗi lần chạy lại: `scripts/kill_sim.sh` (tiến trình sót lại gây lỗi `Frame [map] does not exist`).

## Phần 1 – Mô phỏng

```bash
scripts/kill_sim.sh
scripts/start_sim.sh gui:=true          # gui:=false de chay khong cua so Gazebo (nhanh hon)
scripts/unlock_robot.sh                 # safety_override=backup_only + undock
ros2 launch turtlebot4_viz view_robot.launch.py use_sim_time:=true      # RViz2
scripts/check_topics.sh                 # kiem tra /scan /odom /cmd_vel -> logs/01_topic_check.log
```

## Phần 2 – Dựng bản đồ

```bash
scripts/start_slam.sh                   # SLAM Toolbox (async) voi config/slam_small.yaml
scripts/teleop_slow.sh 0.05 0.2         # lai tay: i , j l k
scripts/save_map.sh                     # -> maps/map.yaml, maps/map.pgm
python3 scripts/clean_map.py            # (tuy chon) loc diem le ngoai tuong; ban goc o maps/map_raw.pgm
```

Bản đồ nộp (`maps/map.pgm`) đã qua `clean_map.py`; bản thô từ SLAM là `maps/map_raw.pgm`.

## Phần 3 – Localization

Dừng SLAM (Ctrl-C), rồi khởi động lại robot:

```bash
scripts/kill_sim.sh
scripts/start_sim.sh gui:=true
scripts/unlock_robot.sh
scripts/start_localization.sh           # map_server + amcl voi maps/map.yaml
ros2 launch turtlebot4_viz view_robot.launch.py use_sim_time:=true
```

Đặt vị trí ban đầu bằng **2D Pose Estimate** trong RViz2, hoặc bằng script:

```bash
python3 scripts/find_pose.py -0.8 0.4 -0.6 0.4     # tim tu the khop scan voi ban do -> "best x y yaw"
python3 scripts/set_initial_pose.py <x> <y> <yaw> 0.15 0.15
python3 scripts/check_localization.py              # in /amcl_pose va do bat dinh
```

Lái nhẹ (`teleop_slow.sh`) để các hạt AMCL hội tụ.

## Phần 4 – Nav2

```bash
scripts/start_nav2.sh                   # nav2.launch.py voi config/nav2.yaml (chay sau localization)
```

Dùng công cụ **Nav2 Goal** trên RViz2 để đặt goal; không điều khiển tay sau đó. Để ghi số liệu (thời gian, quãng đường, khoảng cách tới tường):

```bash
python3 scripts/send_goals.py 3.0,2.0,0.0 2.5,5.6,1.57 -0.4,5.6,3.14 3.5,0.2,0.0
```

Tọa độ trong frame `map`. Mỗi lần chạy ghi quỹ đạo vào một file mới `logs/nav_trajectory_<ngày>_<giờ>.csv`.

## Chụp ảnh cửa sổ RViz2/Gazebo (Wayland)

GNOME trên Wayland chặn chụp màn hình từ terminal. RViz2 và Gazebo chạy qua XWayland nên chụp từng cửa sổ được:

```bash
python3 scripts/shot_window.py rviz figures/anh_rviz.png
python3 scripts/shot_window.py '"Gazebo"' figures/anh_gazebo.png
```

## Cấu trúc

```
launch/    sim_small.launch.py (chinh), sim_maze.launch.py
worlds/    maze_small.sdf, gen_world.py
overlay/   URDF giam tan so cam bien
config/    slam_small.yaml, localization.yaml, nav2.yaml
maps/      map.yaml, map.pgm (+ map_raw.*)
scripts/   cac script chay/kiem tra o tren
logs/      log terminal dung trong bao cao
figures/   hinh dung trong bao cao
report/    report.tex + sections/
```

## Báo cáo

```bash
cd report && xelatex report.tex && xelatex report.tex
```

Cần gói `texlive-xetex`, `texlive-latex-extra`, `texlive-lang-other`, font Liberation và DejaVu Sans Mono.
