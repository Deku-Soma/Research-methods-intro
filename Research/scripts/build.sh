#!/bin/bash
set -e

echo "=========================================="
echo "Building ROS 2 Workspace inside Container"
echo "=========================================="

DOCKER_BIN="${DOCKER_BIN:-docker}"

cd "$(dirname "$0")/../docker"

# Ensure container is running or run via exec / run
$DOCKER_BIN compose run --rm ros2_sim bash -c "
    cd /ros2_ws && \
    source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install && \
    echo 'Build completed successfully!'
"
