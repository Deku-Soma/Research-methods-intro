# RoboCup SSL Differential-Drive Research Simulation (ROS 2 Humble)

This repository contains the complete ROS 2 simulation environment for evaluating a low-cost, 3D-printed differential-drive robotic platform designed for RoboCup Small Size League (SSL) Division B benchmarking.

---

## 1. Overview & Architecture

The system implementation directly mirrors the research proposal and methodology:
* **Robotic Platform**: 100 mm diameter $\times$ 100 mm height cylindrical chassis, dual differential drive spur gear DC motors (50 mm wheels), passive front caster, and centered MPU6050 IMU ($r_{\text{offset}} = 0$).
* **Dual-Loop Control Architecture**:
  * **Laptop Host**: Runs 60 Hz overhead tracking pose receiver and high-level 20–50 Hz Linear Time-Varying Model Predictive Control (LTV-MPC) enforcing SSL constraints ($v \le 1.5\text{ m/s}$, $t_{\text{stop}} \le 2.0\text{ s}$).
  * **Simulated Pico**: Emulates the Raspberry Pi Pico RP2040 dual-core architecture:
    * **Core 0**: micro-ROS subscriber caching trajectory horizons (`TrajectoryProfile.msg`).
    * **Core 1**: High-frequency (200–500 Hz) discrete PID wheel velocity control and fixed-point complementary filter heading fusion.
* **Benchmarking Protocol**: Automated test suite evaluating straight-line 5 m sprint & halt, trajectory tracking RMSE across 3 path geometries (Straight Line, Circular Arc, M-Shape), step-response latency ($\le 16.7\text{ ms}$), and 10-trial consistency standard deviations ($\sigma_x$).

---

## 2. Directory Structure

```
Research/
├── .devcontainer/                  # VS Code Remote Container configuration
│   └── devcontainer.json
├── docker/                         # Docker & noVNC web interface setup
│   ├── Dockerfile                  # ROS 2 Humble + Gazebo + scientific packages
│   ├── docker-compose.yml          # Container configuration (ports 6080, 5901)
│   ├── entrypoint.sh               # Environment sourcing
│   └── start_novnc.sh              # Web-based GUI starter
├── scripts/                        # Automation scripts
│   ├── build.sh                    # Compiles workspace with colcon
│   ├── run_sim.sh                  # Launches Gazebo & noVNC
│   ├── run_benchmarks.sh           # Runs 10-trial automated evaluation
│   └── shell.sh                    # Interactive terminal inside container
├── src/
│   ├── ssl_robot_interfaces/       # Custom ROS 2 messages
│   │   └── msg/
│   │       ├── TrajectoryStep.msg
│   │       ├── TrajectoryProfile.msg
│   │       └── BenchmarkMetric.msg
│   ├── ssl_robot_description/      # URDF / Xacro kinematics & visual models
│   │   ├── urdf/
│   │   │   ├── robot.urdf.xacro
│   │   │   ├── chassis.xacro
│   │   │   ├── wheels.xacro
│   │   │   ├── sensors.xacro       # MPU6050 + modular camera support
│   │   │   └── gazebo.xacro        # Diff-drive, IMU, & 60Hz ground-truth plugins
│   │   ├── rviz/ssl_robot.rviz
│   │   └── launch/display.launch.py
│   ├── ssl_robot_gazebo/           # Simulation worlds & launch files
│   │   ├── worlds/
│   │   │   ├── ssl_field.world     # Official SSL Division B turf & boundary field
│   │   │   └── benchmark_arena.world # 5m sprint lane & M-shape waypoint markers
│   │   └── launch/
│   │       ├── sim.launch.py
│   │       └── ssl_field.launch.py
│   ├── ssl_robot_control/          # Dual-loop control architecture
│   │   ├── ssl_robot_control/
│   │   │   ├── overhead_tracking_node.py  # 60Hz tracking with Gaussian noise
│   │   │   ├── trajectory_generator.py    # Reference path generator
│   │   │   ├── ltv_mpc_planner.py         # Laptop-side constrained MPC optimizer
│   │   │   └── simulated_pico_firmware.py # Pico Core 0 buffer & Core 1 PID
│   │   └── launch/control.launch.py
│   └── ssl_robot_benchmarking/     # Automated evaluation suite
│       ├── ssl_robot_benchmarking/
│       │   ├── sprint_halt_evaluator.py   # v_max, t_stop, d_stop evaluation
│       │   ├── trajectory_evaluator.py    # Path RMSE (E_path) calculation
│       │   ├── latency_evaluator.py       # Step-response command latency
│       │   └── trial_orchestrator.py      # 10-trial statistical batch & consistency
│       └── launch/run_all_benchmarks.launch.py
├── Makefile                        # Quick development targets
└── README.md
```

---

## 3. Quick Start Guide

### Prerequisites
* Docker Desktop installed and running on your Mac.

### Step 1: Start Container & Compile Workspace
Run from the `Research/` directory:
```bash
make build-image   # Builds the multi-arch ROS 2 Humble image
make colcon        # Compiles all packages inside the container
```

### Step 2: Launch Gazebo Simulation with Browser GUI
```bash
make sim
```
Once started, open your web browser to:
👉 **[http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)**

You will see Gazebo and RViz running with the robot loaded in the benchmarking arena!

### Step 3: Run the Benchmarking Suite
To execute the automated 10-trial evaluation:
```bash
make benchmark
```
Results and metrics will be saved to `benchmark_results/benchmark_metrics_summary.csv`.

---

## 4. Overhead Camera Tracking & Optical Vision Extension

The simulation supports two localization modes in `overhead_tracking_node`:
1. **Idealized Ground Truth (Default)**: Leverages Gazebo's 60 Hz 3D position state publisher with calibrated Gaussian sensor noise ($\sigma = 0.001\text{ m}$) injected to model the real-world tracking reality gap.
2. **Optical Camera Mode (Extensible)**: An overhead camera mount is defined in both world files and robot URDF (`sensors.xacro`). When ready, enable optical tracking by passing `tracking_mode:=vision_camera` to `control.launch.py`.

---

## 5. Useful Commands

| Task | Command |
|---|---|
| Open interactive shell in container | `make shell` |
| Launch official SSL match field | `make field` |
| View robot model in RViz | `ros2 launch ssl_robot_description display.launch.py` |
| Stop container | `make down` |
| Clean build artifacts | `make clean` |

# TODO list
* Add the turtle bot and the nvidia bot 
* Add the two bots to the test bench so I can compare results for each robot
* Draw up a comparitive table which documents the results for each robot and an evaluation of which robot performed better in each scenario
