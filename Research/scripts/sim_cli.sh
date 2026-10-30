#!/bin/bash
set -e

# Terminal colors
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

clear
echo -e "${CYAN}${BOLD}===============================================================${NC}"
echo -e "${CYAN}${BOLD}  RoboCup SSL Research Simulation Control Hub${NC}"
echo -e "${CYAN}${BOLD}===============================================================${NC}"
echo -e "Interactive CLI for simulation, baseline benchmarking, and analysis."
echo ""
echo -e "${BOLD}Select an operation:${NC}"
echo -e "  ${GREEN}[1]${NC} Launch Interactive Simulation (Gazebo GUI + RViz)"
echo -e "  ${GREEN}[2]${NC} Run Automated Benchmark Test (Single Platform)"
echo -e "  ${GREEN}[3]${NC} Run Comparative Benchmarks (All 3 Platforms: SSL vs TB3 vs JetBot)"
echo -e "  ${GREEN}[4]${NC} Launch Official RoboCup SSL Match Field"
echo -e "  ${GREEN}[5]${NC} View Benchmark Results (CSV Summaries)"
echo -e "  ${GREEN}[6]${NC} Open Interactive Terminal Inside Container"
echo -e "  ${GREEN}[7]${NC} Stop All Simulation Services and Clean Up"
echo -e "  ${RED}[q]${NC} Quit"
echo ""

read -rp "Enter choice [1-7 or q] (default: 1): " MAIN_CHOICE
MAIN_CHOICE="${MAIN_CHOICE:-1}"

if [[ "$MAIN_CHOICE" =~ ^[qQ]$ ]]; then
    echo "Exiting."
    exit 0
fi

select_robot_model() {
    echo ""
    echo -e "${BOLD}Select Robot Platform:${NC}"
    echo -e "  ${CYAN}[1]${NC} Custom SSL Differential Robot (Standard)"
    echo -e "  ${CYAN}[2]${NC} TurtleBot3 Burger (Commercial Baseline 1)"
    echo -e "  ${CYAN}[3]${NC} NVIDIA JetBot (Commercial Baseline 2)"
    read -rp "Enter choice [1-3] (default: 1): " ROBOT_CHOICE
    case "${ROBOT_CHOICE:-1}" in
        2) SELECTED_ROBOT="turtlebot3_burger" ;;
        3) SELECTED_ROBOT="jetbot" ;;
        *) SELECTED_ROBOT="ssl_robot" ;;
    esac
    echo -e "Selected model: ${GREEN}${SELECTED_ROBOT}${NC}"
}

select_scenario() {
    echo ""
    echo -e "${BOLD}Select Evaluation Scenario:${NC}"
    echo -e "  ${CYAN}[1]${NC} Straight-Line 5m Sprint & Halt"
    echo -e "  ${CYAN}[2]${NC} Circular Arc (Steady-State Radius R=1.0m)"
    echo -e "  ${CYAN}[3]${NC} M-Shape Path (Transient Cornering)"
    read -rp "Enter choice [1-3] (default: 1): " SCENARIO_CHOICE
    case "${SCENARIO_CHOICE:-1}" in
        2) SELECTED_SCENARIO="circular_arc" ;;
        3) SELECTED_SCENARIO="m_shape" ;;
        *) SELECTED_SCENARIO="straight_line" ;;
    esac
    echo -e "Selected scenario: ${GREEN}${SELECTED_SCENARIO}${NC}"
}

select_display_mode() {
    echo ""
    echo -e "${BOLD}Select Display Interface:${NC}"
    echo -e "  ${CYAN}[1]${NC} Native Desktop Window (WSLg / GPU Accelerated, default)"
    echo -e "  ${CYAN}[2]${NC} Web Browser Interface (noVNC at http://localhost:6080/vnc.html)"
    read -rp "Enter choice [1-2] (default: 1): " DISP_CHOICE
    case "${DISP_CHOICE:-1}" in
        2) SELECTED_DISPLAY="novnc" ;;
        *) SELECTED_DISPLAY="auto" ;;
    esac
}

case "$MAIN_CHOICE" in
    1)
        select_robot_model
        select_scenario
        select_display_mode
        echo ""
        echo -e "${BLUE}${BOLD}Starting simulation for [${SELECTED_ROBOT}] on [${SELECTED_SCENARIO}]...${NC}"
        export ROBOT_MODEL="$SELECTED_ROBOT"
        export SCENARIO="$SELECTED_SCENARIO"
        export SIM_DISPLAY_MODE="$SELECTED_DISPLAY"
        "${SCRIPT_DIR}/run_sim.sh"
        ;;

    2)
        select_robot_model
        select_scenario
        echo ""
        echo -e "${BOLD}Enable Gazebo GUI during test?${NC}"
        echo -e "  ${CYAN}[1]${NC} No (Headless fast execution, default)"
        echo -e "  ${CYAN}[2]${NC} Yes (Show visual simulation)"
        read -rp "Enter choice [1-2] (default: 1): " GUI_CHOICE
        case "${GUI_CHOICE:-1}" in
            2) SHOW_GUI="true" ;;
            *) SHOW_GUI="false" ;;
        esac

        echo ""
        echo -e "${BLUE}${BOLD}Executing Benchmark: ${SELECTED_ROBOT} on ${SELECTED_SCENARIO}...${NC}"
        cd "${ROOT_DIR}/docker"
        docker compose up -d
        docker compose exec ros2_sim bash -c "
            source /opt/ros/humble/setup.bash
            if [ -f /ros2_ws/install/setup.bash ]; then
                source /ros2_ws/install/setup.bash
            fi
            ros2 launch ssl_robot_benchmarking run_all_benchmarks.launch.py \
                robot_model:=${SELECTED_ROBOT} \
                scenario:=${SELECTED_SCENARIO} \
                gui:=${SHOW_GUI} \
                total_trials:=1
        "
        echo ""
        echo -e "${GREEN}${BOLD}Benchmark complete. Results updated in benchmark_results/${NC}"
        ;;

    3)
        select_scenario
        echo ""
        echo -e "${BLUE}${BOLD}Running 3-Platform Comparative Suite on scenario: ${SELECTED_SCENARIO}...${NC}"
        "${SCRIPT_DIR}/run_comparative_benchmarks.sh" "$SELECTED_SCENARIO"
        ;;

    4)
        echo ""
        echo -e "${BLUE}${BOLD}Launching Official RoboCup SSL Match Field...${NC}"
        cd "${ROOT_DIR}/docker"
        docker compose up -d
        docker compose exec ros2_sim bash -c "
            source /opt/ros/humble/setup.bash
            source /ros2_ws/install/setup.bash
            ros2 launch ssl_robot_gazebo ssl_field.launch.py
        "
        ;;

    5)
        echo ""
        echo -e "${BOLD}Recent Benchmark Results:${NC}"
        MASTER_CSV="${ROOT_DIR}/benchmark_results/benchmark_comparative_master.csv"
        if [ -f "$MASTER_CSV" ]; then
            echo -e "${CYAN}File: ${MASTER_CSV}${NC}"
            echo "---------------------------------------------------------------"
            cat "$MASTER_CSV"
            echo "---------------------------------------------------------------"
        else
            echo "No benchmark results found yet. Run an evaluation from option [2] or [3]."
        fi
        ;;

    6)
        echo ""
        echo -e "${BLUE}${BOLD}Opening bash terminal in container...${NC}"
        "${SCRIPT_DIR}/shell.sh"
        ;;

    7)
        echo ""
        echo -e "${YELLOW}${BOLD}Stopping all container services...${NC}"
        cd "${ROOT_DIR}/docker"
        docker compose down
        echo -e "${GREEN}Containers stopped and cleaned.${NC}"
        ;;

    *)
        echo -e "${RED}Invalid selection. Exiting.${NC}"
        exit 1
        ;;
esac
