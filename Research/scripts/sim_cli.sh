#!/usr/bin/env bash
# sim_cli.sh - Simulation and Benchmarking CLI

# 1. Source Base ROS 2 distribution if not already active
if ! command -v ros2 &> /dev/null; then
    for distro in humble rolling iron galactic foxy; do
        if [ -f "/opt/ros/$distro/setup.bash" ]; then
            source "/opt/ros/$distro/setup.bash"
            break
        fi
    done
fi

# 2. Source Workspace Underlay/Overlay safely
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$WORKSPACE_DIR/install/setup.bash" ]; then
    source "$WORKSPACE_DIR/install/setup.bash"
fi

ROBOT="${2:-ssl_robot}"
SCENARIO="${3:-straight_line}"
TRIALS="${4:-1}"
GUI="${GUI:-false}"

cleanup_all() {
    pkill -9 -f "gzserver|gzclient" 2>/dev/null || true
    pkill -9 -f "robot_state_publisher|rviz2" 2>/dev/null || true
    pkill -9 -f "ros2 launch" 2>/dev/null || true
    pkill -9 -f "ros2 run" 2>/dev/null || true
    pkill -9 -f "ros2 topic" 2>/dev/null || true
    pkill -9 -f "sprint_halt_evaluator" 2>/dev/null || true
    pkill -9 -f "trajectory_evaluator" 2>/dev/null || true
    pkill -9 -f "trial_orchestrator" 2>/dev/null || true
    pkill -9 -f "ltv_mpc_planner" 2>/dev/null || true
    pkill -9 -f "simulated_pico_firmware" 2>/dev/null || true
    pkill -9 -f "overhead_tracking_node" 2>/dev/null || true
    sleep 1
}

show_help() {
    echo "Usage: ./scripts/sim_cli.sh [command] [robot_model] [scenario] [trials]"
    echo ""
    echo "Commands:"
    echo "  build                                 Build the ROS 2 workspace packages"
    echo "  sim [robot] [scenario]                Launch Gazebo simulation testbed (interactive GUI)"
    echo "  benchmark [robot] [scenario]          Run single trajectory tracking benchmark"
    echo "  batch [robot] [scenario] [trials]     Run repeated batch trials back-to-back"
    echo "  speed_test [robot]                    Run unconstrained top speed & peak acceleration test"
    echo "  speed_test_all                        Run speed test on all 3 platforms"
    echo "  benchmark_all                         Run benchmarks across all 3 platforms"
    echo "  run_all [trials]                      Run all robots back-to-back across all tests with 3D GUI"
    echo "  summary                               Display statistical summary of all recorded trials"
    echo ""
    echo "Robots:     ssl_robot | turtlebot3_burger | jetbot | all"
    echo "Scenarios:  straight_line | circular_arc | m_shape | all"
}

run_speed_test() {
    local target_robot="$1"
    echo "============================================================"
    echo " Starting Straight-Line Speed & Acceleration Test: $target_robot (GUI: $GUI)"
    echo "============================================================"
    
    cleanup_all

    # Launch simulation in background without trajectory controller
    ros2 launch ssl_robot_gazebo sim.launch.py \
        robot_model:="$target_robot" \
        start_control:=false \
        gui:="$GUI" &
    SIM_PID=$!

    echo "Waiting for Gazebo simulation environment to initialize..."
    for i in {1..30}; do
        if ros2 topic list 2>/dev/null | grep -q "/odom"; then
            echo "Simulation is ready. Starting speed evaluator..."
            break
        fi
        sleep 1
    done

    # If GUI is requested, pause briefly so the browser viewer is fully connected before motion starts
    if [ "$GUI" = "true" ]; then
        echo "GUI active: pausing 4 seconds for display stabilization..."
        sleep 4
    fi

    # Run the sprint evaluator in unconstrained mode over 5m
    ros2 run ssl_robot_benchmarking sprint_halt_evaluator \
        --ros-args \
        -p unconstrained:=true \
        -p sprint_distance:=5.0 \
        -p robot_model:="$target_robot"

    kill -SIGINT $SIM_PID 2>/dev/null || true
    sleep 1
    kill -9 $SIM_PID 2>/dev/null || true
    cleanup_all
    echo "Speed test completed for $target_robot. Results logged to benchmark_results/."
}

run_single_trial() {
    local r="$1"
    local s="$2"
    local trial_num="$3"
    local total="$4"
    echo ""
    echo "------------------------------------------------------------"
    echo " [Trial $trial_num / $total] Robot: $r | Scenario: $s (GUI: $GUI)"
    echo "------------------------------------------------------------"
    cleanup_all
    ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py \
        robot_model:="$r" \
        scenario:="$s" \
        gui:="$GUI" \
        total_trials:=1
    cleanup_all
}

run_batch() {
    local target_robot="$1"
    local target_scenario="$2"
    local n_trials="${3:-5}"

    local robots=()
    if [ "$target_robot" = "all" ]; then
        robots=("ssl_robot" "turtlebot3_burger" "jetbot")
    else
        robots=("$target_robot")
    fi

    local scenarios=()
    if [ "$target_scenario" = "all" ]; then
        scenarios=("straight_line" "circular_arc" "m_shape")
    else
        scenarios=("$target_scenario")
    fi

    echo "============================================================"
    echo " Starting Batch Simulation Suite ($n_trials iterations per condition, GUI: $GUI)"
    echo " Robots:    ${robots[*]}"
    echo " Scenarios: ${scenarios[*]}"
    echo "============================================================"

    for r in "${robots[@]}"; do
        for s in "${scenarios[@]}"; do
            for (( i=1; i<=n_trials; i++ )); do
                run_single_trial "$r" "$s" "$i" "$n_trials"
            done
        done
    done

    echo ""
    echo "Batch run completed. Aggregating results..."
    python3 "$WORKSPACE_DIR/scripts/aggregate_benchmarks.py"
}

run_visual_suite() {
    local n_trials="${1:-1}"
    export GUI=true

    echo "============================================================"
    echo " FULL VISUAL DEMONSTRATION & BENCHMARK RECORDING SUITE"
    echo " View 3D Arena Live at: http://localhost:6080/vnc.html"
    echo " Robots:    ssl_robot -> turtlebot3_burger -> jetbot"
    echo " Scenarios: straight_line -> circular_arc -> m_shape -> speed_test"
    echo "============================================================"

    local robots=("ssl_robot" "turtlebot3_burger" "jetbot")
    local scenarios=("straight_line" "circular_arc" "m_shape")

    for r in "${robots[@]}"; do
        echo ""
        echo "############################################################"
        echo " >>> NOW TESTING ROBOT: $r"
        echo "############################################################"

        for s in "${scenarios[@]}"; do
            for (( i=1; i<=n_trials; i++ )); do
                echo ""
                echo "------------------------------------------------------------"
                echo " [VISUAL 3D] Robot: $r | Scenario: $s (Trial $i/$n_trials)"
                echo "------------------------------------------------------------"
                cleanup_all
                ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py \
                    robot_model:="$r" \
                    scenario:="$s" \
                    gui:=true \
                    total_trials:=1
                cleanup_all
                sleep 2
            done
        done

        # Run unconstrained sprint test for this robot
        echo ""
        echo "------------------------------------------------------------"
        echo " [VISUAL 3D] Robot: $r | Test: Straight-Line Speed & Halt"
        echo "------------------------------------------------------------"
        run_speed_test "$r"
        sleep 2
    done

    echo ""
    echo "============================================================"
    echo " All visual test sequences complete! Compiling results..."
    echo "============================================================"
    python3 "$WORKSPACE_DIR/scripts/aggregate_benchmarks.py"
}

case "$1" in
    build)
        cd "$WORKSPACE_DIR"
        colcon build --symlink-install --packages-select ssl_robot_benchmarking ssl_robot_control ssl_robot_description ssl_robot_gazebo
        ;;
    sim)
        cleanup_all
        ros2 launch ssl_robot_gazebo sim.launch.py robot_model:="$ROBOT" scenario:="${SCENARIO:-straight_line}" gui:=true
        ;;
    benchmark)
        cleanup_all
        if [ "$SCENARIO" = "all" ]; then
            for s in straight_line circular_arc m_shape; do
                echo "Running benchmark for $ROBOT on scenario: $s (GUI: $GUI)"
                cleanup_all
                ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py robot_model:="$ROBOT" scenario:="$s" gui:="$GUI"
            done
        else
            ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py robot_model:="$ROBOT" scenario:="$SCENARIO" gui:="$GUI"
        fi
        ;;
    batch)
        run_batch "$ROBOT" "$SCENARIO" "$TRIALS"
        ;;
    speed_test)
        run_speed_test "$ROBOT"
        ;;
    speed_test_all)
        for r in ssl_robot turtlebot3_burger jetbot; do
            run_speed_test "$r"
        done
        ;;
    benchmark_all)
        run_batch "all" "all" "${TRIALS:-3}"
        ;;
    run_all|record_all)
        run_visual_suite "${2:-1}"
        ;;
    summary)
        python3 "$WORKSPACE_DIR/scripts/aggregate_benchmarks.py"
        ;;
    cleanup)
        cleanup_all
        echo "Cleaned up all simulation processes."
        ;;
    *)
        show_help
        ;;
esac
