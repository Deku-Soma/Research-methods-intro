# RoboCup SSL Differential-Drive Research Simulation (ROS 2 Humble)

This directory contains the containerized ROS 2 Humble simulation workspace for evaluating a low-cost, 3D-printed differential-drive robotic platform designed for RoboCup Small Size League (SSL) Division B benchmarking.

---

## 1. Overview & Architecture

The system implementation mirrors the research methodology and physical hardware specifications:
* **Custom Robotic Platform**: 100 mm diameter $\times$ 100 mm height cylindrical chassis, dual differential-drive spur gear DC motors (50 mm wheels, 90 mm track gauge), passive ball caster, and centered MPU6050 IMU.
* **Commercial Baseline Platforms**:
  * **TurtleBot3 (Burger)**: 160 mm track gauge, 66 mm wheels, Dynamixel servomotors, OpenCR microcontroller.
  * **NVIDIA JetBot**: 110 mm track gauge, 65 mm wheels, TT micro gearmotors.
* **Dual-Loop Control Architecture**:
  * **Central Host (Laptop)**: Runs 60 Hz overhead tracking pose receiver and high-level 20–50 Hz Linear Time-Varying Model Predictive Control (LTV-MPC) enforcing SSL constraints ($v \le 1.5\text{ m/s}$, $t_{\text{stop}} \le 2.0\text{ s}$).
  * **Simulated Pico (RP2040 Firmware)**: Emulates the physical dual-core architecture:
    * **Core 0**: micro-ROS subscriber caching trajectory horizons (`TrajectoryProfile.msg`).
    * **Core 1**: High-frequency (200–500 Hz) discrete PID wheel velocity control and complementary filter heading fusion.
* **Benchmarking Protocol**: Automated test suite evaluating straight-line 5 m sprint & halt, trajectory tracking RMSE across 3 path geometries (Straight Line, Circular Arc, M-Shape), step-response latency ($\le 16.7\text{ ms}$), and 10-trial consistency standard deviations ($\sigma_x$).

---

## 2. Directory Structure

```
Research/
├── .devcontainer/                  # VS Code Remote Container configuration
│   └── devcontainer.json
├── docker/                         # Docker & noVNC web interface setup
│   ├── Dockerfile                  # ROS 2 Humble + Gazebo + scientific packages (OSQP, CVXPY)
│   ├── docker-compose.yml          # Container configuration (ports 6080, 5901)
│   ├── entrypoint.sh               # Environment sourcing
│   └── start_novnc.sh              # Web-based GUI starter
├── scripts/                        # Automation scripts
│   ├── detect_hardware.sh          # Probes GPU, WSLg, X11, and writes compose overrides
│   ├── build.sh                    # Compiles workspace with colcon inside container
│   ├── run_sim.sh                  # Launches Gazebo & visual GUI
│   ├── run_benchmarks.sh           # Runs single-platform automated evaluation
│   ├── run_comparative_benchmarks.sh # Runs 3-platform comparative evaluation
│   ├── sim_cli.sh                  # Interactive Bash CLI for Linux / WSL
│   └── shell.sh                    # Interactive terminal inside container
├── sim_cli.ps1                     # Interactive Windows PowerShell simulation CLI
├── Makefile                        # Quick development targets
├── todo.md                         # Milestone tracking and architectural review tasks
├── src/
│   ├── ssl_robot_interfaces/       # Custom ROS 2 messages
│   │   └── msg/
│   │       ├── TrajectoryStep.msg      # Single trajectory point (x, y, theta, v, omega)
│   │       ├── TrajectoryProfile.msg   # Horizon of trajectory steps
│   │       └── BenchmarkMetric.msg     # Trial performance metrics
│   ├── ssl_robot_description/      # URDF / Xacro kinematics & visual models
│   │   ├── urdf/
│   │   │   ├── robot.urdf.xacro        # Custom 3D-printed SSL robot
│   │   │   ├── turtlebot3_burger.urdf.xacro # TurtleBot3 Burger baseline
│   │   │   ├── jetbot.urdf.xacro       # NVIDIA JetBot baseline
│   │   │   ├── chassis.xacro
│   │   │   ├── wheels.xacro
│   │   │   ├── sensors.xacro           # MPU6050 + modular camera support
│   │   │   └── gazebo.xacro            # Diff-drive, IMU, & 60Hz ground-truth plugins
│   │   ├── rviz/ssl_robot.rviz
│   │   └── launch/display.launch.py
│   ├── ssl_robot_gazebo/           # Simulation worlds & launch files
│   │   ├── worlds/
│   │   │   ├── ssl_field.world         # Official SSL Division B turf & boundary field
│   │   │   └── benchmark_arena.world   # 5m sprint lane & M-shape waypoint markers
│   │   └── launch/
│   │       ├── sim.launch.py           # Main simulation launcher (robot_model, scenario)
│   │       └── ssl_field.launch.py     # Match field launcher
│   ├── ssl_robot_control/          # Dual-loop control architecture
│   │   ├── ssl_robot_control/
│   │   │   ├── overhead_tracking_node.py  # 60Hz tracking with Gaussian sensor noise
│   │   │   ├── trajectory_generator.py    # Reference path generator
│   │   │   ├── ltv_mpc_planner.py         # Central host constrained MPC optimizer
│   │   │   └── simulated_pico_firmware.py # Pico Core 0 buffer & Core 1 PID controller
│   │   └── launch/control.launch.py
│   └── ssl_robot_benchmarking/     # Automated evaluation suite
│       ├── ssl_robot_benchmarking/
│       │   ├── sprint_halt_evaluator.py   # v_max, t_stop, d_stop evaluation
│       │   ├── trajectory_evaluator.py    # Path RMSE (E_path) calculation
│       │   ├── latency_evaluator.py       # Step-response command latency
│       │   └── trial_orchestrator.py      # Multi-trial statistical batch aggregator
│       └── launch/run_all_benchmarks.launch.py
└── benchmark_results/              # Output CSV metrics (created upon test execution)
    ├── benchmark_metrics_summary.csv
    └── benchmark_comparative_master.csv
```

---

## 3. Quick Start Guide

### Step 1: Launch via Interactive Control Hub

#### Windows (PowerShell):
```powershell
.\sim_cli.ps1
```

#### Linux / WSL (Bash):
```bash
make cli
```
Or:
```bash
./scripts/sim_cli.sh
```

The interactive menu provides guided prompts to configure robot platform, path geometry, display interface, and benchmarking parameters.

---

### Step 2: Launch via Make Targets

#### Visual Simulation
```bash
make sim                                # Custom SSL robot on straight-line course
make sim ROBOT=turtlebot3_burger        # TurtleBot3 Burger baseline
make sim ROBOT=jetbot SCENARIO=m_shape  # JetBot on M-shape course
```

#### Official RoboCup SSL Match Field
```bash
make field
```

#### Single-Platform Automated Benchmark (10 Trials)
```bash
make benchmark ROBOT=ssl_robot SCENARIO=straight_line
```

#### Comparative Baseline Benchmarking (All 3 Platforms)
```bash
make benchmark-all SCENARIO=straight_line
make benchmark-all SCENARIO=circular_arc
make benchmark-all SCENARIO=m_shape
```

---

## 4. Hardware Detection & Display Modes

The simulation automatically probes host display capabilities through `scripts/detect_hardware.sh`:

1. **Windows WSLg (Default on Windows 11)**:
   * Direct hardware acceleration using the host graphics card (NVIDIA RTX/GTX or Intel/AMD).
   * Renders Gazebo and RViz directly as native Windows desktop windows.
2. **Native Linux X11 / DRI**:
   * Direct X11 socket forwarding with OpenGL DRI passthrough.
3. **Web Browser Interface (noVNC Fallback)**:
   * Accessible at **http://localhost:6080/vnc.html**.
   * Ideal for headless servers or remote access.
   * Can be forced explicitly at any time:
     ```bash
     make novnc
     ```

---

## 5. Control System Topics & Node Interfaces

```
Topic Name                       Type                                 Publisher                   Subscriber
-------------------------------------------------------------------------------------------------------------------------
/overhead_tracking/pose          geometry_msgs/msg/PoseStamped        overhead_tracking_node      ltv_mpc_planner, evaluators
/trajectory/reference_profile    ssl_robot_interfaces/TrajectoryProfile trajectory_generator        ltv_mpc_planner
/pico/trajectory_horizon         ssl_robot_interfaces/TrajectoryProfile ltv_mpc_planner             simulated_pico_firmware (Core 0)
/imu/data                        sensor_msgs/msg/Imu                  gazebo imu plugin           simulated_pico_firmware (Core 1)
/odom                            nav_msgs/msg/Odometry                gazebo diff-drive plugin    simulated_pico_firmware (Core 1)
/cmd_vel                         geometry_msgs/msg/Twist              simulated_pico_firmware     gazebo diff-drive plugin
/benchmark/metrics               ssl_robot_interfaces/BenchmarkMetric evaluators                  trial_orchestrator
```

---

## 6. Supported Evaluation Scenarios

| Scenario Identifier | Trajectory Description | Key Evaluated Metrics |
| :--- | :--- | :--- |
| `straight_line` | 5.0 m linear sprint from origin to $(5.0, 0.0)$, followed by halt command. | $v_{\text{max}}$, acceleration, $t_{\text{stop}}$, $d_{\text{stop}}$ |
| `circular_arc` | Steady-state circle of radius $R = 1.0\text{ m}$ centered at $(1.0, 0.0)$. | Steady-state tracking error, lateral centrifugal slip |
| `m_shape` | Multi-waypoint course: $(0,0) \to (1.5, 2.0) \to (3.0, 0.5) \to (4.5, 2.0) \to (6.0, 0.0)$. | Transient cornering overshoot, yaw response, path RMSE |

---

## 7. Results & Output Formats

Execution data is exported to `benchmark_results/`:

* **`benchmark_metrics_summary.csv`**: Contains run-by-run metrics:
  ```csv
  trial_number,scenario,v_max_mps,stopping_time_s,stopping_distance_m,latency_ms,path_rmse_m,lateral_excursion_m
  ```

* **`benchmark_comparative_master.csv`**: Master log recording multi-trial statistical aggregates across all platforms:
  ```csv
  timestamp,robot_model,scenario,num_trials,v_max_mean,v_max_std,t_stop_mean,t_stop_std,d_stop_mean,d_stop_std,path_rmse_mean,path_rmse_std,latency_mean,latency_std
  ```

---

## 8. Development & Maintenance Commands

| Action | Command |
| :--- | :--- |
| Open interactive container bash shell | `make shell` |
| Recompile ROS 2 packages inside container | `make colcon` |
| Rebuild Docker container image | `make build-image` |
| Stop container services | `make down` |
| Clean Colcon build, install, log, and Python cache | `make clean` |
| Inspect detected display configuration | `make detect-hw` |
