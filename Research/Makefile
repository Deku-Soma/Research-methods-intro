# Makefile for ROS 2 RoboCup SSL Simulation

DOCKER_BIN ?= docker
COMPOSE_DIR = docker
ROBOT ?= ssl_robot
SCENARIO ?= straight_line

.PHONY: help build build-image colcon up down sim field benchmark benchmark-all shell clean detect-hw gpu novnc cli

help:
	@echo "==============================================================="
	@echo "RoboCup SSL Differential Robot - ROS 2 Simulation Control"
	@echo "==============================================================="
	@echo "  make cli           - Launch interactive CLI prompt for simulation"
	@echo "  make build         - Build docker container and colcon workspace"
	@echo "  make build-image   - Build Docker image from Dockerfile"
	@echo "  make colcon        - Run colcon build inside container"
	@echo "  make up            - Start container (auto-detects GPU & display)"
	@echo "  make gpu           - Force GPU-accelerated native window display"
	@echo "  make novnc         - Force noVNC web browser interface"
	@echo "  make detect-hw     - Probe hardware (GPU/WSLg/X11) and show config"
	@echo "  make down          - Stop container services"
	@echo "  make sim [ROBOT=x] - Launch Gazebo simulation (ssl_robot, turtlebot3_burger, jetbot)"
	@echo "  make field         - Launch official RoboCup SSL match field"
	@echo "  make benchmark     - Run benchmark suite for ROBOT (default: ssl_robot)"
	@echo "  make benchmark-all - Run comparative benchmarks across all 3 platforms"
	@echo "  make shell         - Open interactive bash terminal in container"
	@echo "  make clean         - Clean colcon build/install/log directories"
	@echo "==============================================================="

detect-hw:
	./scripts/detect_hardware.sh

gpu:
	./scripts/detect_hardware.sh wslg
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose up -d

novnc:
	./scripts/detect_hardware.sh novnc
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose up -d

build-image:
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose build

up: detect-hw
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose up -d

down:
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose down

colcon: up
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose exec ros2_sim bash -c \
		"source /opt/ros/humble/setup.bash && cd /ros2_ws && colcon build --symlink-install"

build: build-image colcon

sim: up
	ROBOT_MODEL=$(ROBOT) ./scripts/run_sim.sh

field: up
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose exec ros2_sim bash -c \
		"source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash && ros2 launch ssl_robot_gazebo ssl_field.launch.py"

benchmark: up
	ROBOT_MODEL=$(ROBOT) SCENARIO=$(SCENARIO) ./scripts/run_benchmarks.sh

benchmark-all: up
	./scripts/run_comparative_benchmarks.sh $(SCENARIO)

shell: up
	./scripts/shell.sh

cli:
	./scripts/sim_cli.sh

clean:
	rm -rf build install log benchmark_results
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
