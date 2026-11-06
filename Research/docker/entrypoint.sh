#!/bin/bash
set -e

# Source ROS 2 Humble base installation
source /opt/ros/humble/setup.bash

# Source workspace install if available
if [ -f "/ros2_ws/install/setup.bash" ]; then
    source /ros2_ws/install/setup.bash
fi

exec "$@"
