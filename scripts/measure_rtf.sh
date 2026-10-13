#!/usr/bin/env bash
# Do he so thoi gian thuc (sim s / wall s) cua mo phong va tan so /scan.
source /opt/ros/humble/setup.bash
sim_sec() { ros2 topic echo /clock --once 2>/dev/null | awk '/sec:/ {print $2; exit}'; }
S1=$(sim_sec); W1=$(date +%s)
sleep "${1:-30}"
S2=$(sim_sec); W2=$(date +%s)
echo "sim: $S1 -> $S2 ; wall: $W1 -> $W2"
echo "real-time factor ~ $(( (S2 - S1) * 100 / (W2 - W1) )) %"
echo "tan so /scan:"
timeout 10 ros2 topic hz /scan --window 5 2>&1 | tail -3
