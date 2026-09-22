#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"
if ! command -v "$DOCKER_BIN" &> /dev/null; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

cd "$(dirname "$0")/../docker"

echo "=========================================================="
echo "Executing Automated Benchmarking Suite (10 Trials Batch)"
echo "=========================================================="

$DOCKER_BIN compose up -d

$DOCKER_BIN compose exec ros2_sim bash -c "
    source /opt/ros/humble/setup.bash
    if [ -f /ros2_ws/install/setup.bash ]; then
        source /ros2_ws/install/setup.bash
    fi
    ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py scenario:=straight_line gui:=false
"
