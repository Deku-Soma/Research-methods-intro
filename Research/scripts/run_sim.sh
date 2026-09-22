#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"
if ! command -v "$DOCKER_BIN" &> /dev/null; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

cd "$(dirname "$0")/../docker"

echo "=========================================================="
echo "Starting ROS 2 Simulation with noVNC Web Interface"
echo "=========================================================="
echo "1. Web Interface will be available at:"
echo "   --> http://localhost:6080/vnc.html <--"
echo "2. Starting container services..."

$DOCKER_BIN compose up -d

echo ""
echo "Waiting 3 seconds for virtual display initialization..."
sleep 3

echo "Launching Gazebo simulation inside container..."
$DOCKER_BIN compose exec ros2_sim bash -c "
    source /opt/ros/humble/setup.bash
    if [ -f /ros2_ws/install/setup.bash ]; then
        source /ros2_ws/install/setup.bash
    fi
    ros2 launch ssl_robot_gazebo sim.launch.py gui:=true rviz:=true
"
