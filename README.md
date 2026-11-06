# Bridging the Cost Barrier: A Simulation-Based Feasibility Study of a 3D-Printed ROS 2 Platform for RoboCup SSL Benchmarking

This repository contains the containerized ROS 2 Humble simulation workspace, benchmarking suite, and dynamic models evaluating the feasibility of an accessible, 3D-printed differential-drive robotic platform for RoboCup Small Size League (SSL) Division B benchmarking.

---

## 1. Overview & Research Framing

RoboCup Small Size League (SSL) Division B participation traditionally requires specialized omnidirectional drive mechanisms, custom brushless motors, and proprietary software architectures costing tens of thousands of Rands per unit. This research investigates whether an accessible differential-drive platform fabricated with additive manufacturing (3D printing) and operated under open-source Robot Operating System 2 (ROS 2) and micro-ROS middleware can satisfy SSL kinematic, trajectory-tracking, and safety constraints.

### Hardware Status & Simulation Scoping
Structural CAD geometry, electronic schematics, and component selections were designed to conform strictly with official SSL size envelopes ($\le 180\text{ mm}$ diameter, $\le 150\text{ mm}$ height). Due to external supply chain delays in physical component procurement, the physical platform parameters directly establish the dynamic configuration of the high-fidelity Gazebo simulation testbed. Consequently, empirical benchmarks evaluate platform dynamics, control stability, and regulatory compliance in simulation rather than on physical hardware.

### Key System Specifications
* **Custom Robotic Platform**: Cylindrical PLA chassis ($100\text{ mm}$ diameter $\times 100\text{ mm}$ height, mass $m = 0.435\text{ kg}$, yaw inertia $I_z = 5.44 \times 10^{-4}\text{ kg}\cdot\text{m}^2$), dual spur gear DC motors ($50\text{ mm}$ wheels, $90\text{ mm}$ track gauge, integrated magnetic quadrature encoders), passive ball caster, and centered MPU6050 IMU.
* **Commercial Baseline Platforms**:
  * **TurtleBot3 Burger**: Academic research baseline ($160\text{ mm}$ track gauge, $66\text{ mm}$ wheels, Dynamixel XL430 servomotors with $0.22\text{ m/s}$ firmware velocity limit, OpenCR microcontroller).
  * **NVIDIA JetBot**: Embedded AI baseline ($110\text{ mm}$ track gauge, $65\text{ mm}$ wheels, open-loop micro TT gearmotors without encoder feedback).
* **Hierarchical Dual-Loop Control Architecture**:
  * **Central Host Workstation**: Executes an overhead tracking pose subscriber ($60\text{ Hz}$) and a constrained Error-Model Linear Time-Varying Model Predictive Control (LTV-MPC) solver operating at $20\text{ Hz}$ ($\Delta t = 50\text{ ms}$, lookahead horizon $N = 5$) to enforce SSL velocity caps ($v \le 1.50\text{ m/s}$ referee Stop speed cap) and deceleration profiles ($t_{\text{stop}} \le 2.0\text{ s}$).
  * **Microcontroller Firmware (Simulated RP2040 Pico)**:
    * **Core 0**: micro-ROS subscriber buffering incoming trajectory profile horizons (`TrajectoryProfile.msg`).
    * **Core 1**: High-frequency ($500\text{ Hz}$) discrete PID wheel velocity control loop and complementary filter heading estimation.

### Evaluated Hypotheses & Summary Results
1. **Regulatory Compliance (H1a)**: The platform enforces the referee Stop command speed ceiling ($1.50\text{ m/s}$) and decelerates from $1.50\text{ m/s}$ to zero velocity in $0.80\text{ s}$ under maximum braking, comfortably inside the $2.0\text{ s}$ league Halt threshold.
2. **Dynamic Capability (H1b)**: In unconstrained sprint evaluations without MPC bounds, the spur gear DC motors reach a terminal velocity of $2.001\text{ m/s}$ and peak linear acceleration of $3.0\text{ m/s}^2$, confirming that the drive mechanism provides dynamic capability exceeding SSL requirements.
3. **Trajectory Tracking Performance**: Across standardized path geometries, the custom platform achieves orthogonal tracking RMSE ($E_{\text{path}}$) of $0.0145\text{ m}$ (Straight-Line), $0.0218\text{ m}$ (Circular Arc), and $0.0238\text{ m}$ (M-Shape). On steady-state circular arcs, the platform outperforms the TurtleBot3 Burger ($0.1437\text{ m}$) by a factor of 6.59 because the TurtleBot3 suffers actuator velocity clipping at $0.22\text{ m/s}$.
4. **Command Latency & Stability (H2)**: Systematic injection of command delays ($\tau_d \in \{0, 10, 20, 40\}\text{ ms}$) demonstrates that tracking remains stable when communication latency is maintained below the $16.7\text{ ms}$ ($60\text{ Hz}$) vision frame interval. Delays of $20\text{ ms}$ and $40\text{ ms}$ degrade path error by $32\%$ and $118\%$ respectively due to phase lag.

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
│   ├── aggregate_benchmarks.py     # Aggregates multi-trial statistics (Mean ± SD)
│   ├── sim_cli.sh                  # Simulation and benchmarking CLI for Linux / WSL
│   └── shell.sh                    # Interactive terminal inside container
├── sim_cli.ps1                     # Native Windows PowerShell simulation and benchmark CLI
├── system_architecture.mmd         # System architecture flowchart (Mermaid)
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
    ├── benchmark_comparative_master.csv  # Raw trial log with RMSE, speed, and stopping metrics
    ├── benchmark_statistical_summary.csv # Aggregated Mean ± SD matrix and pass rates
    └── benchmark_summary_table.csv       # Formatted multi-platform summary table
```

---

## 3. Simulation & Benchmarking CLI Reference

The workspace includes a command-line interface implemented for PowerShell (`sim_cli.ps1`) and Bash (`scripts/sim_cli.sh`). The CLI manages Docker services, launches Gazebo simulations, executes multi-trial benchmark suites, and calculates summary statistics.

### PowerShell CLI (Windows)

Execute commands from the `Research/` directory or root workspace:

```powershell
.\sim_cli.ps1 <command> [robot] [scenario] [-Trials <N>] [-Gui]
```

#### Command Summary

| Command | Arguments / Flags | Description |
| :--- | :--- | :--- |
| `run_all` | `[trials]` | Executes all robot platforms across all scenarios with 3D GUI enabled. Opens the browser viewer with a 6-second delay to begin screen recording. |
| `record_all` | `[trials]` | Alias for `run_all`. |
| `batch` | `-Robot <R> -Scenario <S> -Trials <N> [-Gui]` | Runs repeated trials back-to-back for a target platform and path geometry. |
| `speed_test` | `-Robot <R> [-Gui]` | Evaluates unconstrained straight-line acceleration and terminal velocity over 5 meters without MPC limits. |
| `speed_test_all` | `[-Gui]` | Executes unconstrained straight-line speed tests across all three robot platforms sequentially. |
| `benchmark` | `-Robot <R> -Scenario <S> [-Gui]` | Executes a single trajectory evaluation trial with live tracking RMSE telemetry. |
| `benchmark_all` | `[-Trials <N>] [-Gui]` | Executes the complete matrix of all robots across all trajectory scenarios. |
| `summary` | *(none)* | Calculates sample count, Mean $\pm$ SD, and pass rates from recorded trials and displays the summary table. |
| `sim` | `-Robot <R> -Scenario <S>` | Launches interactive Gazebo simulation and opens the 3D browser viewer. |
| `build` | *(none)* | Compiles ROS 2 packages inside the container with colcon. |
| `shell` | *(none)* | Opens an interactive bash shell inside the simulation container. |

#### Example Invocations

```powershell
# Run the complete visual test suite for screen recording
.\sim_cli.ps1 run_all 3

# Execute 10 headless batch trials on the custom SSL robot
.\sim_cli.ps1 batch -Robot ssl_robot -Scenario m_shape -Trials 10

# Execute batch trials with live 3D visualization
.\sim_cli.ps1 batch -Robot turtlebot3_burger -Scenario circular_arc -Trials 5 -Gui

# Run unconstrained terminal speed tests
.\sim_cli.ps1 speed_test -Robot ssl_robot -Gui
.\sim_cli.ps1 speed_test_all

# Print the statistical Mean ± SD summary table
.\sim_cli.ps1 summary
```

### Linux / WSL Bash CLI

The Linux CLI provides equivalent functionality using positional arguments:

```bash
# Full visual recording sequence
./scripts/sim_cli.sh run_all 3

# Batch testing
./scripts/sim_cli.sh batch ssl_robot m_shape 10

# Unconstrained speed testing
./scripts/sim_cli.sh speed_test ssl_robot
./scripts/sim_cli.sh speed_test_all

# Trajectory benchmark
./scripts/sim_cli.sh benchmark jetbot circular_arc

# Statistical aggregation
./scripts/sim_cli.sh summary
```

---

## 4. Visual Simulation & Screen Recording via noVNC

The simulation container renders 3D graphics through a virtual X11 framebuffer (`Xvfb :1`) paired with an internal VNC server (`x11vnc`) and WebSocket proxy (`websockify`). This configuration provides responsive 3D simulation streaming without host display server configuration:

* **Browser Access URL**: [http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)
* **Automatic Launch**: Specifying `-Gui` on any command or invoking `sim` or `run_all` automatically opens the default web browser to this address.
* **Connection**: Click the **Connect** button on the page to display the live Gazebo arena.
* **Video Screen Recording**:
  * Windows Game Bar: Press `Win + Alt + R` to start or stop recording the browser window.
  * OBS Studio: Add a **Window Capture** source targeting the browser tab displaying the noVNC stream.
  * Automated Delay: The `run_all` and `record_all` commands insert a 6-second countdown before simulation initialization, allowing the operator to focus the browser and begin recording.

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
| `straight_line` | 5.0 m linear sprint from $(0,0)$ to $(5.0, 0.0)$ under LTV-MPC, followed by halt command. | $v_{\text{max}}$, acceleration, $t_{\text{stop}}$, $d_{\text{stop}}$, path RMSE |
| `circular_arc` | Continuous curvature circle of radius $R = 1.0\text{ m}$ centered at $(1.0, 0.0)$. | Steady-state tracking error, lateral centrifugal slip, path RMSE |
| `m_shape` | Waypoint course: $(0,0) \to (1.5, 2.0) \to (3.0, 0.5) \to (4.5, 2.0) \to (6.0, 0.0)$. | Transient cornering overshoot, yaw response, path RMSE |
| `speed_test` | Unconstrained 5.0 m linear run at maximum motor torque without MPC saturation limits. | Physical platform terminal velocity, peak linear acceleration |

---

## 7. Results & Output Formats

Benchmark trials record telemetry and performance data to `benchmark_results/`:

### Raw Comparative Log (`benchmark_comparative_master.csv`)
Records each executed trial as an individual row with metrics including:
```csv
timestamp,robot_model,scenario,run_duration_s,v_max,t_stop,d_stop,path_rmse,passed
2026-10-31 13:40:22,ssl_robot,Trajectory: m_shape,22.14,0.485,0.000,0.000,0.0762,True
```

### Statistical Summary Table (`benchmark_statistical_summary.csv`)
Aggregated through `scripts/aggregate_benchmarks.py` (or `.\sim_cli.ps1 summary`), computing sample statistics for each platform and scenario pair:
```csv
robot_model,scenario,trials_count,path_rmse_mean_sd,v_max_mean_sd,t_stop_mean_sd,d_stop_mean_sd,pass_rate_pct
ssl_robot,m_shape,3,0.0772 ± 0.0009,0.485 ± 0.000,N/A,N/A,100.0%
ssl_robot,straight_line,5,0.0142 ± 0.0018,1.488 ± 0.012,0.360 ± 0.020,0.228 ± 0.014,100.0%
turtlebot3_burger,straight_line,3,0.0195 ± 0.0006,0.220 ± 0.000,0.180 ± 0.000,0.038 ± 0.000,100.0%
jetbot,straight_line,3,0.0210 ± 0.0008,0.350 ± 0.000,0.210 ± 0.010,0.045 ± 0.002,100.0%
```

---

## 8. Development & Maintenance Commands

| Action | Command |
| :--- | :--- |
| Open interactive container bash shell | `.\sim_cli.ps1 shell` or `make shell` |
| Recompile ROS 2 packages inside container | `.\sim_cli.ps1 build` or `make colcon` |
| Terminate lingering simulation processes | `.\sim_cli.ps1 cleanup` |
| Rebuild Docker container image | `make build-image` |
| Stop container services | `make down` |
| Clean Colcon build, install, log, and Python cache | `make clean` |
| Inspect detected display configuration | `make detect-hw` |

---

## 9. Citation & Repository Reference

To cite this study or software suite:

```bibtex
@misc{ssl_robot_code_2026,
  title        = {{RoboCup SSL} 3D-Printed Differential-Drive Simulation and Benchmarking Suite},
  author       = {Samlal, Sashin},
  year         = {2026},
  howpublished = {\url{https://github.com/Deku-Soma/Research-methods-intro}},
  note         = {Software repository and experimental simulation datasets}
}
```
