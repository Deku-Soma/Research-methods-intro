#!/bin/bash
set -e

DOCKER_BIN="${DOCKER_BIN:-docker}"
MODELS=("ssl_robot" "turtlebot3_burger" "jetbot")
SCENARIO="${1:-straight_line}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../docker"

echo "================================================================="
echo "RoboCup SSL Comparative Baseline Benchmarking"
echo "Comparing: Custom SSL Robot vs TurtleBot3 Burger vs NVIDIA JetBot"
echo "Scenario: $SCENARIO"
echo "================================================================="

$DOCKER_BIN compose up -d

for MODEL in "${MODELS[@]}"; do
    echo ""
    echo "-----------------------------------------------------------------"
    echo "Starting 10-trial benchmark evaluation for: $MODEL"
    echo "-----------------------------------------------------------------"
    
    $DOCKER_BIN compose exec ros2_sim bash -c "
        source /opt/ros/humble/setup.bash
        if [ -f /ros2_ws/install/setup.bash ]; then
            source /ros2_ws/install/setup.bash
        fi
        ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py robot_model:=$MODEL scenario:=$SCENARIO gui:=false
    "
done

echo ""
echo "================================================================="
echo "All comparative trials complete. Master log written to:"
echo "/ros2_ws/benchmark_results/benchmark_comparative_master.csv"
echo "================================================================="
