#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"

ROBOT_MODEL="${ROBOT_MODEL:-ssl_robot}"
SCENARIO="${SCENARIO:-straight_line}"

cd "$(dirname "$0")/../docker"

echo "=========================================================="
echo "Executing Automated Benchmarking Suite (10 Trials Batch)"
echo "Robot Model : $ROBOT_MODEL"
echo "Scenario    : $SCENARIO"
echo "=========================================================="

$DOCKER_BIN compose up -d

$DOCKER_BIN compose exec ros2_sim bash -c "
    source /opt/ros/humble/setup.bash
    if [ -f /ros2_ws/install/setup.bash ]; then
        source /ros2_ws/install/setup.bash
    fi
    killall -q -9 gzserver gzclient robot_state_publisher 2>/dev/null || true
    sleep 1
    ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py robot_model:=$ROBOT_MODEL scenario:=$SCENARIO gui:=false
"
