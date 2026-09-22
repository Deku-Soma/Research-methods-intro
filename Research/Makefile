# Makefile for ROS 2 RoboCup SSL Simulation

DOCKER_BIN ?= $(shell which docker 2>/dev/null || echo "/Applications/Docker.app/Contents/Resources/bin/docker")
COMPOSE_DIR = docker

.PHONY: help build build-image colcon up down sim field benchmark shell clean

help:
	@echo "==============================================================="
	@echo "RoboCup SSL Differential Robot - ROS 2 Simulation Control"
	@echo "==============================================================="
	@echo "  make build       - Build docker container and colcon workspace"
	@echo "  make build-image - Build Docker image from Dockerfile"
	@echo "  make colcon      - Run colcon build inside container"
	@echo "  make up          - Start background container & noVNC service"
	@echo "  make down        - Stop container services"
	@echo "  make sim         - Launch Gazebo simulation & open noVNC"
	@echo "  make field       - Launch official RoboCup SSL match field"
	@echo "  make benchmark   - Run automated 10-trial benchmark suite"
	@echo "  make shell       - Open interactive bash terminal in container"
	@echo "  make clean       - Clean colcon build/install/log directories"
	@echo "==============================================================="
	@echo "noVNC Browser UI: http://localhost:6080/vnc.html"
	@echo "==============================================================="

build-image:
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose build

up:
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose up -d

down:
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose down

colcon: up
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose exec ros2_sim bash -c \
		"source /opt/ros/humble/setup.bash && cd /ros2_ws && colcon build --symlink-install"

build: build-image colcon

sim: up
	@echo ">>> Open your browser at http://localhost:6080/vnc.html to view Gazebo & RViz <<<"
	./scripts/run_sim.sh

field: up
	@echo ">>> Open your browser at http://localhost:6080/vnc.html to view the SSL field <<<"
	cd $(COMPOSE_DIR) && $(DOCKER_BIN) compose exec ros2_sim bash -c \
		"source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash && ros2 launch ssl_robot_gazebo ssl_field.launch.py"

benchmark: up
	./scripts/run_benchmarks.sh

shell: up
	./scripts/shell.sh

clean:
	rm -rf build install log benchmark_results
