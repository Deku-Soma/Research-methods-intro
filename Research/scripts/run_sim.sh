#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/detect_hardware.sh"

cd "${SCRIPT_DIR}/../docker"

echo "=========================================================="
echo "Starting ROS 2 Simulation Services..."
echo "=========================================================="

$DOCKER_BIN compose up -d

echo ""
echo "Waiting 2 seconds for services to initialize..."
sleep 2

ROBOT_MODEL="${ROBOT_MODEL:-ssl_robot}"
SCENARIO="${SCENARIO:-straight_line}"

echo "Launching Gazebo simulation ($ROBOT_MODEL, scenario: $SCENARIO) inside container..."
$DOCKER_BIN compose exec ros2_sim bash -c "
    source /opt/ros/humble/setup.bash
    if [ -f /ros2_ws/install/setup.bash ]; then
        source /ros2_ws/install/setup.bash
    fi
    ros2 launch ssl_robot_gazebo sim.launch.py robot_model:=$ROBOT_MODEL scenario:=$SCENARIO gui:=true rviz:=true
"
