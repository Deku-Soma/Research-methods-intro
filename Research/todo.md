# Research Review and Amendments Task List

This document tracks identified gaps, architectural reviews, and planned amendments for the RoboCup SSL differential-drive research project. It bridges the academic research proposal with the simulation and hardware implementations.

---

## 1. Comparative Baseline Integration

The research proposal commits to benchmarking the custom 3D-printed platform against two commercial baselines: the TurtleBot and the NVIDIA JetBot.

- [x] **Import TurtleBot3 Simulation Model**: Added `turtlebot3_burger.urdf.xacro` with accurate kinematics (160mm wheel separation, 66mm wheel diameter, 1.0kg mass) and Gazebo plugins.
- [x] **Import NVIDIA JetBot Simulation Model**: Added `jetbot.urdf.xacro` with physical parameters (110mm track gauge, 65mm wheel diameter, 0.9kg mass, TT DC motor limits) and Gazebo plugins.
- [x] **Standardize Robot State Interfaces**: Unified `/cmd_vel`, `/odom`, `/imu/data`, and `/overhead_tracking/pose` across all three models with identical joint names (`left_wheel_joint`, `right_wheel_joint`).
- [x] **Multi-Model Batch Benchmarking**: Configured `trial_orchestrator.py`, `run_all_benchmarks.launch.py`, `sim.launch.py`, and `control.launch.py` with `robot_model` support; added `run_comparative_benchmarks.sh` and `make benchmark-all` / `make benchmark ROBOT=<model>`.
- [x] **Draft Specification Comparison Table**: Documented specifications and LaTeX booktabs code in `Research proposal/baseline_comparison_table.md` for proposal integration.

---

## 2. Firmware Emulation and Control Loop Fidelity

The physical prototype uses a Raspberry Pi Pico (RP2040) running micro-ROS, splitting work between Core 0 (network buffer) and Core 1 (sensor fusion and PID). The current simulation emulates this using a Python ROS 2 node (`simulated_pico_firmware.py`).

- [ ] **Validate Quantization and Motor Dynamics**: Incorporate encoder tick quantization, PWM frequency limits, and motor deadband into the firmware simulation loop to model realistic hardware behavior.
- [ ] **Micro-ROS C++ Firmware Integration**: Decide whether to maintain the Python simulation node for high-level validation or compile native C++ micro-ROS client code targeting POSIX/Gazebo for closer hardware parity.
- [ ] **Core-to-Core Mailbox Timing**: Verify that trajectory horizon caching on Core 0 and high-frequency PID execution on Core 1 match the microsecond scheduling budgets in the proposal.

---

## 3. Trajectory Generation and Path Scenarios

The current test suite covers straight-line sprint, circular arc, and an M-shape course.

- [ ] **Kinematic Feasibility Verification**: Verify that the trajectory generator respects non-holonomic velocity bounds ($v \le 1.5\text{ m/s}$, $\omega \le 6.0\text{ rad/s}$) at all waypoint transitions to avoid artificial tracking error spikes.
- [ ] **Review Additional Evaluation Trajectories**: Consider adding an S-curve, high-frequency slalom, or defensive side-to-side evasion path to better represent SSL Division B gameplay.
- [ ] **Waypoint Marker Visualization**: Ensure Gazebo visual markers in `benchmark_arena.world` match the exact coordinates defined in `trajectory_generator.py`.

---

## 4. LTV-MPC Planner Optimization and Constraints

The high-level controller uses an Error-Model Linear Time-Varying Model Predictive Control (LTV-MPC) running at 20 Hz to 50 Hz on the central host.

- [ ] **Constraint Enforcement**: Confirm that acceleration limits ($\alpha_{\text{max}} = 2.5\text{ m/s}^2$) strictly guarantee the RoboCup SSL 2.0-second halting rule under all initial entry speeds.
- [ ] **Execution Latency Profiling**: Profile the OSQP QP-solve time per iteration to verify that optimization calculations execute within the 20 ms to 50 ms time budget without causing scheduling jitter.
- [ ] **Tracking Error Horizon Tuning**: Fine-tune the prediction horizon length ($N = 5$) and state weighting matrices ($Q, R$) to eliminate overshoot during sharp path transients.

---

## 5. Experimental Protocols and Reality Gap Validation

- [ ] **Realistic Vision Sensor Noise**: Calibrate the Gaussian noise parameters in `overhead_tracking_node.py` against published empirical accuracy figures for overhead SSL-Vision systems.
- [ ] **Automated Data Export Pipeline**: Standardize the output format of `trial_orchestrator.py` to produce combined CSV summaries and LaTeX-ready comparative tables.
- [ ] **Document Consistency Audit**: Cross-reference mathematical equations, notation, and parameter values in `Research proposal/main.tex` with the implementation files in `Research/src/`.
