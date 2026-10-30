# RoboCup SSL Differential-Drive Research Repository

University of the Witwatersrand, Johannesburg  
School of Computer Science and Applied Mathematics  
Honours Research Project (2026)

---

## 1. Research Overview

This repository hosts the complete academic and computational work for investigating the viability of a low-cost, 3D-printed differential-drive robotic platform for the RoboCup Small Size League (SSL) Division B.

Standard SSL platforms utilize omnidirectional drive mechanisms and custom brushless motors that cost tens of thousands of Rands per robot. This cost establishes an economic barrier to entry that excludes under-resourced universities and schools, especially within the South African context. This research assesses whether non-holonomic differential-drive kinematics, governed by a dual-loop control architecture (laptop-side Linear Time-Varying Model Predictive Control and embedded microcontroller discrete PID), can satisfy SSL Division B operational constraints ($v \le 1.5\text{ m/s}$, $t_{\text{stop}} \le 2.0\text{ s}$).

The project evaluates the custom 3D-printed robot against two established commercial differential-drive baselines:
1. **TurtleBot3 (Burger)**: The academic research standard for indoor SLAM and navigation.
2. **NVIDIA JetBot**: A widely deployed educational platform with open-loop DC actuators.

---

## 2. Repository Layout

```
Research methods intro/
├── README.md                           # Master repository documentation (this file)
├── .gitignore                          # Clean repository ignores (LaTeX, Python, Colcon)
│
├── Research/                           # ROS 2 Humble & Gazebo Simulation Environment
│   ├── README.md                       # Simulation technical documentation
│   ├── Makefile                        # Build, launch, simulation, and benchmark targets
│   ├── sim_cli.ps1                     # Interactive Windows PowerShell simulation CLI
│   ├── docker/                         # Multi-arch Docker setup with WSLg GPU & noVNC
│   │   ├── Dockerfile                  # ROS 2 Humble desktop + Gazebo + OSQP/CVXPY
│   │   ├── docker-compose.yml          # Container service definition
│   │   ├── entrypoint.sh               # Environment sourcing
│   │   └── start_novnc.sh              # Web GUI launcher
│   ├── scripts/                        # Automation scripts
│   │   ├── detect_hardware.sh          # Auto-probes GPU, WSLg, X11, or noVNC
│   │   ├── build.sh                    # Colcon compilation script
│   │   ├── run_sim.sh                  # Interactive visual simulation launcher
│   │   ├── run_benchmarks.sh           # Single-robot batch benchmark evaluator
│   │   ├── run_comparative_benchmarks.sh # 3-platform comparative benchmark suite
│   │   ├── sim_cli.sh                  # Interactive Linux/WSL Bash simulation CLI
│   │   └── shell.sh                    # Interactive shell inside the container
│   ├── src/                            # ROS 2 Packages
│   │   ├── ssl_robot_interfaces/       # Custom messages (TrajectoryProfile, BenchmarkMetric)
│   │   ├── ssl_robot_description/      # URDF/Xacro models (SSL Robot, TurtleBot3, JetBot)
│   │   ├── ssl_robot_gazebo/           # Worlds (benchmark_arena.world, ssl_field.world)
│   │   ├── ssl_robot_control/          # LTV-MPC planner, overhead tracker, Pico firmware
│   │   └── ssl_robot_benchmarking/     # Automated evaluators (sprint, path, latency)
│   └── todo.md                         # Research amendment and milestone tracking
│
├── Research proposal/                  # Research Proposal & Honours Report (LaTeX)
│   ├── main.tex                        # Proposal source document
│   ├── thesis.tex                      # Extended Honours report / thesis document
│   ├── references.bib                  # BibTeX bibliography
│   ├── makefile                        # Document compilation and clean targets
│   ├── build.bat                       # Windows latexmk build script
│   ├── baseline_comparison_table.md    # Kinematic & empirical comparison data
│   └── Models/                         # OpenSCAD 3D chassis mechanical designs
│
├── Lit_review/                         # Literature Review Source Document (LaTeX)
│   ├── main.tex                        # Literature review manuscript
│   ├── references.bib                  # Domain bibliography
│   └── makefile                        # Literature review build targets
│
├── Annotated_Bibliography__1_/         # Annotated Bibliography Source Document (LaTeX)
│   ├── main.tex                        # Annotated bibliography manuscript
│   └── references.bib                  # Core bibliography
│
├── research papers/                    # Reference Archive (TDPs, Control Theory, Benchmarks)
│   ├── 2025_TDP_First-Order.pdf
│   ├── 2024_TDP_The-Bots(low cost and 3d printed parts).pdf
│   ├── 2023_TDP_The_A_Team.pdf
│   ├── sslrules.pdf
│   └── ... (20+ foundational research papers)
│
├── python skills/                      # Research Automation Scripts
│   └── comments_extraction.py          # Extracts reviewer feedback annotations from PDFs
│
└── .agents/                            # Coding agent instructions, rules, and review skills
```

---

## 3. System Architecture & Control Pipeline

The simulation architecture mirrors the physical hardware design:

```
[Central Host / Laptop]
   │
   ├── Overhead Tracking Node (60 Hz) ──> /overhead_tracking/pose (Global x, y, theta)
   │
   ├── Trajectory Generator (20 Hz)   ──> /trajectory/reference_profile
   │
   └── LTV-MPC Planner (20-50 Hz)     ──> /pico/trajectory_horizon (TrajectoryProfile.msg)
                                            │
                                            ▼
[Simulated RP2040 Pico Firmware Node]
   │
   ├── Core 0 (Network Buffer): Subscribes to horizon, validates timestamps
   │
   └── Core 1 (200-500 Hz Execution Loop):
         ├── Heading Fusion (Complementary Filter: IMU + Odometry)
         └── Discrete PID Wheel Controllers ──> /cmd_vel (v, omega)
                                                   │
                                                   ▼
[Gazebo Simulation World]
   ├── Diff-Drive Physics Plugin
   ├── Centered MPU6050 IMU Plugin
   └── Ground Truth State Publisher (60 Hz)
```

### Evaluated Robot Platforms

| Metric | Custom SSL Robot | TurtleBot3 Burger | NVIDIA JetBot |
| :--- | :--- | :--- | :--- |
| **Chassis Profile** | Cylinder ($\varnothing 100 \times 100\text{ mm}$) | Tiered ($\varnothing 138 \times 192\text{ mm}$) | Box ($138 \times 115 \times 80\text{ mm}$) |
| **Total Mass** | $0.435\text{ kg}$ | $1.000\text{ kg}$ | $0.900\text{ kg}$ |
| **Track Gauge ($b$)** | $90\text{ mm}$ ($0.090\text{ m}$) | $160\text{ mm}$ ($0.160\text{ m}$) | $110\text{ mm}$ ($0.110\text{ m}$) |
| **Wheel Radius ($r$)** | $25\text{ mm}$ ($0.025\text{ m}$) | $33\text{ mm}$ ($0.033\text{ m}$) | $32.5\text{ mm}$ ($0.0325\text{ m}$) |
| **Max Linear Speed** | $1.50\text{ m/s}$ (Division B Limit) | $0.22\text{ m/s}$ | $0.35\text{ m/s}$ |
| **Max Wheel Torque** | $2.00\text{ N}\cdot\text{m}$ | $1.40\text{ N}\cdot\text{m}$ | $0.45\text{ N}\cdot\text{m}$ |
| **Microcontroller** | Raspberry Pi Pico (RP2040) | OpenCR 1.0 (ARM Cortex-M7) | None (Jetson Nano GPIO) |
| **Estimated Cost** | R 1,500 - R 2,200 | R 11,000 - R 14,000 | R 3,500 - R 4,500 |

---

## 4. Quick Start: Running the Simulation

### Prerequisites
* **Windows 10/11**: Docker Desktop running with WSL2 backend.
* **Linux / Ubuntu**: Docker engine and Docker Compose plugin installed.

### Option A: Windows PowerShell Interactive CLI (Recommended)

From the project root on Windows:
```powershell
.\Research\sim_cli.ps1
```
The menu allows you to:
1. Launch interactive Gazebo GUI + RViz (with platform and scenario selection).
2. Run single-robot automated 10-trial benchmarks.
3. Run the complete 3-platform comparative benchmark suite across SSL Robot, TurtleBot3, and JetBot.
4. Launch the official RoboCup SSL match field.
5. Display CSV summary tables directly in the terminal.
6. Open an interactive shell inside the container.
7. Stop all simulation services and clean up containers.

### Option B: Linux / WSL Interactive Bash CLI

From the `Research/` directory:
```bash
cd Research
make cli
```
Or directly:
```bash
./scripts/sim_cli.sh
```

### Option C: Direct Makefile Commands

| Command | Action |
| :--- | :--- |
| `make build` | Builds Docker image and compiles ROS 2 workspace |
| `make up` | Starts container (auto-detects WSLg / GPU / noVNC) |
| `make sim` | Launches Gazebo simulation with custom SSL robot |
| `make sim ROBOT=turtlebot3_burger` | Launches simulation with TurtleBot3 Burger |
| `make sim ROBOT=jetbot` | Launches simulation with NVIDIA JetBot |
| `make field` | Launches official RoboCup SSL match field |
| `make benchmark` | Runs 10-trial evaluation on custom SSL robot |
| `make benchmark ROBOT=jetbot SCENARIO=m_shape` | Runs benchmark on specific platform and path |
| `make benchmark-all` | Runs full 3-platform comparative benchmark suite |
| `make shell` | Opens interactive bash shell inside container |
| `make down` | Stops all container services |
| `make clean` | Removes Colcon build, install, log, and cache files |

### Display Modes
The simulation automatically selects the best visual interface:
1. **Windows WSLg (Default on Windows 11)**: Renders native desktop windows with direct GPU acceleration.
2. **Web Browser (noVNC Fallback)**: Accessible at `http://localhost:6080/vnc.html` without requiring any local X server configuration.

To force browser mode:
```bash
make novnc
```

---

## 5. Benchmarking Protocols & Scenarios

The automated evaluation suite tests three path geometries:

1. **Straight-Line Sprint & Halt (`straight_line`)**:
   * Evaluates top acceleration, steady-state velocity, and braking compliance with the SSL 2.0-second halting rule ($t_{\text{stop}} \le 2.0\text{ s}$).
2. **Circular Arc Tracking (`circular_arc`)**:
   * Assesses steady-state centrifugal tracking accuracy and lateral drift under continuous curvature ($R = 1.0\text{ m}$).
3. **M-Shape Course (`m_shape`)**:
   * Stresses transient response across sharp yaw transitions and acute waypoint changes.

### Benchmark Output Files
Evaluation logs and aggregated metrics are saved to `Research/benchmark_results/`:
* `benchmark_metrics_summary.csv`: Single-run metrics containing $v_{\text{max}}$, $t_{\text{stop}}$, $d_{\text{stop}}$, latency, and path RMSE ($E_{\text{path}}$).
* `benchmark_comparative_master.csv`: Multi-robot comparative log recording mean ($\mu$) and standard deviation ($\sigma_x$) across 10-trial sequences.

---

## 6. Document Compilation (LaTeX)

### Research Proposal & Thesis
Navigate to `Research proposal/`:
```bash
cd "Research proposal"
make thesis       # Compiles thesis.tex -> thesis.pdf
make proposal     # Compiles main.tex -> main.pdf
make clean        # Removes auxiliary build files (*.aux, *.log, *.bbl)
```
On Windows without Make, run:
```cmd
build.bat
```

### Literature Review
Navigate to `Lit_review/`:
```bash
cd Lit_review
make              # Compiles main.tex -> main.pdf
```

---

## 7. Repository Cleanliness & Maintenance

The repository uses strict `.gitignore` rules to keep version control clean:
* LaTeX build artifacts (`*.aux`, `*.bbl`, `*.fls`, `*.log`, `*.out`, `*.toc`, `*.synctex.gz`) are excluded.
* Python compilation artifacts (`__pycache__/`, `*.pyc`) are excluded.
* ROS 2 build directories (`build/`, `install/`, `log/`, `benchmark_results/`) are excluded.
* OS-specific metadata (`.DS_Store`, `Thumbs.db`) is excluded.

To clean the simulation workspace at any time:
```bash
cd Research
make clean
```
To clean LaTeX build files:
```bash
cd "Research proposal"
make clean
```
