# Implementation Plan for Addressing Advisor Comments

This document outlines the proposed changes to the honors research proposal to address the feedback in `comments.json`, incorporating technical improvements for a dual-loop control architecture on the Raspberry Pi Pico and the central laptop.

## 1. Context Alignment

All comments are mapped to the primary LaTeX file `Research proposal/main.tex`. The table below links each comment to its exact location in the source code:

| Comment ID | PDF Page | Comment Description | Referenced Text  Area in Source | Source Location (Line numbers) |
|---|---|---|---|---|
| 1 | 5 | Add precise research questions / scenarios to end of Introduction | End of Chapter 1 | After L206 (before L208) |
| 2 | 7 | Refine control framing to integrate both PID and MPC | "PID or MPC" | L268 |
| 3 | 9 | Distinguish low-cost educational platforms from competition SSL robots | Section 3.3 (Accessibility through Cost Optimization) | L328-333 |
| 4 | 12 | Add problem statement, research questions, and hypotheses section | End of Chapter 1 | After L206 (before L208) |
| 5 | 13 | Correct PID feedback source (encoders vs. MPU6050 accelerometer) | Controller feedback description | L346-347, L384 |
| 6 | 14 | Restructure Benchmarking section into Scenarios and Metrics | Section 4.3 (Benchmarking Protocols) | L386-427 |
| 7 | 14 | Avoid overlap of "PWM Signals" in Figure 4.1 | TikZ system diagram | L354-378 |
| 8 | 14 | Document calibration, synchronization, and logging protocols | Section 4.3 (Benchmarking Protocols) | L386-427 |
| 9 | 14 | Include JetBot as a third baseline alongside TurtleBot | Section 4.3 (Benchmarking Protocols) | L388 |
| 10 | 14 | Standardize software stack description on ROS 2 (remove ROS 1 "master") | Section 4.2 (Distributed Software Stack) | L350-353, L364 |
| 11 | 15 | Justify M-shaped trajectory and introduce multiple path classes | L402 (M-shaped path description) | L402-404 |
| 12 | 17 | Extend the optimistic schedule of work to match full honors timeline | Chapter 5 (Workplan) table and text | L430-449 |

## 2. Integrity Checks and Secondary Impacts

* **Dual-Loop Control Architecture**: Instead of removing Model Predictive Control (MPC) from the framing, the project is updated to implement a dual-loop control architecture. A high-level Linear Time-Varying Model Predictive Control (LTV-MPC) running on the laptop calculates target trajectories, while a low-level Proportional-Integral-Derivative (PID) loop running on the Raspberry Pi Pico regulates motor speeds to track those trajectories. This resolves the concern in Comment 2.
* **Dual-Core Processing Split**: The Raspberry Pi Pico will utilize both processing cores to prevent timing conflicts. Core 1 is dedicated to high-frequency sensor reading (encoders and IMU) and PID motor execution, while Core 0 handles low-speed micro-ROS communication and trajectory buffering. This split protects the critical motor interrupt routines from being delayed by network communication.
* **Quadrature Encoders Integration**: Specifying that the local wheel-velocity PID controller uses quadrature encoder feedback rather than the MPU6050 accelerometer is mathematically correct. This change has a secondary impact on Chapter 4: the MPU6050 is reassigned to body-frame linear acceleration and yaw rate tracking sent to the central host, and a new quadrature encoder variable is introduced. We must verify that the kinematic update equations in Section 2.1 (L239-247) and error equations in Section 4.2 (L380-384) remain consistent with this.
* **ROS 2 Communication Paradigm**: Standardizing on ROS 2 requires removing the concept of a centralized "ROS master node" (which is unique to ROS 1). The central laptop will instead run a standard ROS 2 node communicating via a micro-ROS Agent. Figure 4.1 must be updated to replace the "ROS Master" label with "ROS 2 Nodes" and include a "micro-ROS Agent" bridging block.
* **Academic Style and Consistency**: All changes must adhere to Wits research methods guidelines, including parenthetical citation formats `\citep{}` and narrative format `\citet{}`, present tense for author references, and complete avoidance of AI-signature terms.

## 3. Detailed Implementation Plan

The proposed modifications will be made to `Research proposal/main.tex` and `Research proposal/references.bib`.

### Chapter 1: Introduction
* **Modification**: Insert a new Section 1.1 `\section{Problem Statement and Research Questions}` at the end of the chapter (after L206).
* **Changes**:
  * Establish the problem statement: physical and financial barriers to entering the RoboCup SSL due to expensive holonomic platforms, and the need to verify if low-cost differential-drive platforms can meet competitive constraints.
  * Formulate one primary research question: Can a low-cost, 3D-printed differential-drive platform running under a dual-loop LTV-MPC and discrete PID control stack satisfy the motion and safety requirements defined by the RoboCup SSL Division B technical standards?
  * Formulate two secondary research questions focusing on: (1) the impact of non-holonomic kinematics on path fidelity across distinct trajectory classes, and (2) the timing latency and scheduling jitter of the ROS 2 and micro-ROS communication bridge.
  * State the corresponding hypotheses: (1) the robot can achieve a maximum velocity of $1.5\text{ m/s}$ and stop within the $2.0\text{ s}$ limit, and (2) communication latencies will remain below the $16.7\text{ ms}$ threshold required for 60Hz SSL-Vision frames.

### Chapter 2: Background
* **Modification (L268)**: Update the text to explain the dual-loop control framing.
* **Changes**: Frame the temporal constraints around the combination of high-level LTV-MPC (on the laptop) and low-level PID (on the Pico) working in tandem, rather than presenting them as mutually exclusive options.

### Chapter 3: Related Work
* **Modification (L328-333)**: Expand Section 3.3 (Accessibility through Cost Optimization) to contrast educational and competition platforms.
  * *Draft Content*: Add a paragraph outlining that while educational platforms like the TurtleBot focus on low-speed navigation in static environments, competition-grade SSL robots demand high velocities, high accelerations, and sub-millisecond latencies. Explain how the proposed platform addresses this gap by testing a cheap, accessible design against strict SSL constraints.

### Chapter 4: Methodology
The methodology will be expanded to include the four new technical phases detailing the dual-core implementation and the MPC design.

#### Phase 3.1: Hardware Integration & Core-1 Sensor Fusion
* **GY-521 Physical Alignment**: The GY-521 breakout board (housing the MPU6050) is mounted precisely at the geometric center of the drive-wheel axle line. This eliminates false centripetal acceleration readings:
  $$a_y = \omega_z^2 \cdot r_{\text{offset}}$$
  where $r_{\text{offset}} = 0$.
* **Non-Blocking I2C Driver**: The microcontroller runs a non-blocking $I^2C$ polling routine using Direct Memory Access (DMA) clocked at $400\text{ kHz}$ (Fast Mode) on Core 1. This isolates the sensor reads, ensuring the Pico does not drop time-critical wheel encoder interrupts.
* **Local Complementary Filter**: Core 1 runs a fixed-point Complementary Filter to fuse sensor data:
  $$\theta_{\text{fused}} = \alpha \cdot (\theta_{\text{prev}} + \omega_z \cdot \Delta t) + (1 - \alpha) \cdot \theta_{\text{accel}}$$
  This mitigates gyroscopic thermal drift. The fused heading is passed to Core 0 via the hardware FIFO mailbox.

#### Phase 3.2: Custom micro-ROS Network Configuration
* **Custom Message Interface (`TrajectoryProfile.msg`)**: A dedicated ROS 2 message is defined to hold the future trajectory steps computed by the MPC solver, keeping the wireless payload minimal:
  ```msg
  # TrajectoryStep.msg
  float32 v_target
  float32 omega_target
  uint32 delta_ms
  ```
* **Best-Effort Quality of Service (QoS)**: The micro-ROS publisher for IMU and odometry data on the Pico is configured to use a Best-Effort transport policy. This prevents dropped Wi-Fi packets from triggering retransmission cycles, isolating the control loop from network jitter.
* **Time Synchronization Service**: The Pico runs the `rmw_uros_epoch_nanos()` time service client on Core 0 to continuously sync its internal clock with the laptop's master ROS 2 clock, enabling microsecond-accurate timestamp alignment for latency logging.

#### Phase 3.3: Laptop-Side MPC Development & Linearization
* **Kinematic Plant Linearization**: The laptop runs an Error-Model Linear Time-Varying Model Predictive Control (LTV-MPC) node written in C++ using the `OsqpEigen` or `Acados` solver. The non-holonomic differential kinematics are linearized around the reference path at every camera tracking frame update.
* **Constraint Mapping**: The physical RoboCup SSL Division B boundary limits are programmed directly into the MPC optimization matrix:
  * Velocity bounds: $-1.5\text{ m/s} \le v_k \le 1.5\text{ m/s}$.
  * Acceleration bounds ($\alpha_{\text{max}}$) are calculated to satisfy the $2.0\text{-second}$ safety halting requirement ($t_{\text{stop}}$).

#### Phase 3.4: Low-Level Kinematic Tracking & PID Execution
* **Trajectory Horizon Buffer**: Core 0 of the Pico receives the incoming array of 5–10 trajectory steps from the laptop and caches them sequentially in a local buffer.
* **Feedforward + Feedback Interpolation**: Core 1 extracts the active trajectory target, calculates the target wheel velocities via inverse kinematics, and feeds the value directly into the PID loop. Core 1 runs at $200\text{ Hz} - 500\text{ Hz}$ (much higher than the laptop's MPC loop frequency of $20\text{ Hz} - 50\text{ Hz}$) and linearly interpolates intermediate steps to guarantee smooth motor speed transitions.
* **PID Feedback (L384)**: Update the error term of the PID loop to represent the difference between target and measured wheel angular velocities: $e(t) = \dot{\phi}_{\text{target}}(t) - \dot{\phi}_{\text{measured}}(t)$, where $\dot{\phi}_{\text{measured}}$ is obtained from the quadrature encoders.

#### Figure 4.1 (L354-378)
* Update the TikZ code to show:
  * "Central Laptop (ROS 2 Navigation Nodes & LTV-MPC Solver)"
  * "Pico Core 0 (micro-ROS Client & Trajectory Buffer)"
  * "Pico Core 1 (Sensor Fusion & 500Hz PID Control Loop)"
  * Reposition the "PWM Signals" label to `node[below]` to prevent overlap.

### Chapter 5: Workplan
* **Schedule Revision (Table 5.1 / L430)**: Extend the timeline from August 30 to October 25 to allow for a realistic honors project duration, incorporating the new development phases for dual-core firmware and C++ LTV-MPC.

### References Bibliography
* **Modification (`references.bib`)**: Add a `@misc` citation for the NVIDIA JetBot developer guide and references for the OSQP/Acados solvers.

## 4. Assumptions and Limitations

* **Assumptions**:
  * The physical laboratory and overhead tracking system remain available throughout the project duration.
  * The overhead camera provides consistent 60Hz position updates with minimal occlusion.
  * Standard consumer 3D-printing materials (PLA) provide sufficient structural rigidity to withstand collision forces.
* **Limitations**:
  * The study is limited to differential-drive kinematics and does not evaluate holonomic (omni-directional or mecanum) drive mechanisms.
  * The testing will be performed on a flat carpet surface and may not generalize to other turf or field materials.
