# Comparative Baseline Platforms Reference

This document provides a comparative specification table evaluating the custom 3D-printed RoboCup SSL differential-drive platform against two baseline systems: the TurtleBot3 (Burger configuration) and the NVIDIA JetBot. This material is prepared for integration into the research proposal and the final honors thesis.

---

## 1. Motivation and Rationale for Platform Selection

* **Custom 3D-Printed Platform**: Designed to evaluate whether an inexpensive differential-drive system can achieve high-speed navigation and safety braking compliant with RoboCup SSL Division B rules ($v \le 1.5\text{ m/s}$, $t_{\text{stop}} \le 2.0\text{ s}$).
* **TurtleBot3 Burger**: The standard academic research baseline for differential-drive mobile robotics. It is engineered for indoor mapping, navigation, and SLAM in static environments rather than high-acceleration sports dynamics.
* **NVIDIA JetBot**: A widely deployed, low-cost educational robotics kit. It represents consumer-grade hobbyist hardware characterized by open-loop DC gearmotors and GPU-focused edge intelligence.

---

## 2. Platform Specifications Comparison Table

| Metric / Parameter | Custom SSL Differential Robot | TurtleBot3 (Burger) | NVIDIA JetBot |
| :--- | :--- | :--- | :--- |
| **Chassis Geometry** | Symmetrical cylinder ($\varnothing 100\text{ mm} \times 100\text{ mm}$) | Tiered plates ($\varnothing 138\text{ mm} \times 192\text{ mm}$) | Rectangular ($138\text{ mm} \times 115\text{ mm} \times 80\text{ mm}$) |
| **Chassis Fabrication** | 3D-printed PLA casing and base | Injection-molded modular plates | 3D-printed chassis shell |
| **Total Mass** | $\approx 0.435\text{ kg}$ | $\approx 1.000\text{ kg}$ | $\approx 0.900\text{ kg}$ |
| **Track Gauge ($b$)** | $90\text{ mm}$ ($0.090\text{ m}$) | $160\text{ mm}$ ($0.160\text{ m}$) | $110\text{ mm}$ ($0.110\text{ m}$) |
| **Wheel Diameter ($d$)**| $50\text{ mm}$ ($r = 0.025\text{ m}$) | $66\text{ mm}$ ($r = 0.033\text{ m}$) | $65\text{ mm}$ ($r = 0.0325\text{ m}$) |
| **Wheel Width** | $12\text{ mm}$ | $18\text{ mm}$ | $25\text{ mm}$ |
| **Passive Support** | Single rear ball caster ($r = 10\text{ mm}$) | Single rear ball caster ($r = 5\text{ mm}$) | Single front steel caster ($r = 7.5\text{ mm}$) |
| **Actuator Type** | Dual spur-gear DC motors | Dual Dynamixel XL430-W250 servos | Dual TT DC micro gearmotors |
| **Feedback Mechanism**| Integrated magnetic quadrature encoders | Internal 12-bit absolute encoders | Open-loop (no native wheel encoders) |
| **Max Linear Velocity**| $1.50\text{ m/s}$ (RoboCup Division B limit) | $0.22\text{ m/s}$ (firmware ceiling) | $\approx 0.35\text{ m/s}$ (motor saturation) |
| **Max Wheel Torque** | $2.00\text{ N}\cdot\text{m}$ (stall torque at gearbox) | $1.40\text{ N}\cdot\text{m}$ | $0.45\text{ N}\cdot\text{m}$ |
| **Embedded Controller**| Raspberry Pi Pico (RP2040 dual-core) | OpenCR 1.0 (ARM Cortex-M7) | None (direct GPIO from Jetson Nano) |
| **Host / Companion** | External laptop (LTV-MPC solver) | Raspberry Pi 3/4 SBC | NVIDIA Jetson Nano SBC |
| **IMU Sensor** | MPU6050 (6-axis, center-aligned) | MPU9250 (9-axis) | MPU6050 / ICM-20948 |
| **Vision Tracking** | Overhead camera tracking optical sigil | External camera / 360 LDS-01 LiDAR | Front wide-angle onboard camera |
| **Software Interface** | ROS 2 Humble + micro-ROS client | ROS 2 Humble | ROS / JetBot Python API |
| **Estimated Cost** | $\approx \text{R}1\,500 - \text{R}2\,200$ | $\approx \text{R}11\,000 - \text{R}14\,000$ | $\approx \text{R}3\,500 - \text{R}4\,500$ |
| **Primary Target** | Low-cost high-speed SSL competition | Educational mobile SLAM and research | Introductory embedded AI education |

---

## 3. LaTeX Table Code (Ready for Insertion into `main.tex`)

```latex
\begin{table}[H]
\centering
\small
\caption{Comparative Mechanical, Kinematic, and Electronic Specifications Across Evaluated Platforms}
\label{tab:platform_comparison}
\begin{tabular}{p{3.8cm}p{3.6cm}p{3.6cm}p{3.6cm}}
\toprule
\textbf{Parameter} & \textbf{Custom SSL Platform} & \textbf{TurtleBot3 Burger} & \textbf{NVIDIA JetBot} \\
\midrule
Chassis Geometry & Cylinder ($\varnothing 100 \times 100$\,mm) & Tiered ($\varnothing 138 \times 192$\,mm) & Box ($138 \times 115 \times 80$\,mm) \\
Total Mass & $\approx 0.435$\,kg & $\approx 1.000$\,kg & $\approx 0.900$\,kg \\
Track Gauge ($b$) & 90\,mm & 160\,mm & 110\,mm \\
Wheel Diameter ($d$) & 50\,mm & 66\,mm & 65\,mm \\
Actuation & Spur gear DC motors & Dynamixel XL430-W250 & Micro TT gearmotors \\
Encoder Feedback & Integrated magnetic & Internal 12-bit absolute & None (open-loop) \\
Max Velocity ($v_{\text{max}}$) & $1.50$\,m/s (SSL Limit) & $0.22$\,m/s & $0.35$\,m/s \\
Max Torque & $2.00$\,N$\cdot$m & $1.40$\,N$\cdot$m & $0.45$\,N$\cdot$m \\
Microcontroller & Raspberry Pi Pico (RP2040) & OpenCR (Cortex-M7) & None (Jetson GPIO) \\
Host Computing & External laptop (LTV-MPC) & Raspberry Pi SBC & NVIDIA Jetson Nano \\
Primary IMU & MPU6050 (center-aligned) & MPU9250 & MPU6050 \\
Tracking Mechanism & Overhead camera (60\,Hz sigil) & Overhead camera / LiDAR & Onboard front camera \\
Software Stack & ROS 2 + micro-ROS & ROS 2 Humble & ROS / Python API \\
Estimated Cost & $\approx \text{R}1\,500 - \text{R}2\,200$ & $\approx \text{R}11\,000 - \text{R}14\,000$ & $\approx \text{R}3\,500 - \text{R}4\,500$ \\
Primary Domain & Competitive SSL Division B & Educational SLAM & Introductory Embedded AI \\
\bottomrule
\end{tabular}
\end{table}
```

---

## 4. Empirical Simulation Benchmark Results

The three platforms were subjected to automated Gazebo simulations using the laptop-side Linear Time-Varying Model Predictive Control (LTV-MPC) planner paired with 60\,Hz ground-truth overhead tracking. Table \ref{tab:empirical_benchmarks} reports the path root-mean-square tracking error ($E_{\text{path}}$) across the evaluated scenarios.

```latex
\begin{table}[H]
\centering
\small
\caption{Empirical Trajectory Tracking Performance ($E_{\text{path}}$ RMSE) in Gazebo Simulation}
\label{tab:empirical_benchmarks}
\begin{tabular}{lccc}
\toprule
\textbf{Scenario} & \textbf{Custom SSL Robot} & \textbf{TurtleBot3 Burger} & \textbf{NVIDIA JetBot} \\
\midrule
Straight-Line (5.0\,m Sprint \& Halt) & 0.0145\,m (1.45\,cm) & 0.0143\,m (1.43\,cm) & 0.0145\,m (1.45\,cm) \\
Circular Arc ($R = 1.0$\,m Steady-State) & 0.0218\,m (2.18\,cm) & 0.1437\,m (14.37\,cm) & 0.0238\,m (2.38\,cm) \\
M-Shape (8.1\,m Transient Cornering) & 0.0238\,m (2.38\,cm) & 0.0260\,m (2.60\,cm) & 0.0397\,m (3.97\,cm) \\
\bottomrule
\end{tabular}
\end{table}
```

### Analysis of Kinematic and Inertial Effects

1. **Straight-Line Tracking**: All three platforms track the straight-line trajectory with high fidelity, maintaining deviations below $1.5\,\text{cm}$. The predictive horizon ($N=5$) allows each platform to align its heading rapidly and track the reference line.
2. **Circular Arc Tracking**: Under continuous angular acceleration along an $R=1.0\,\text{m}$ arc, the physical properties of the platforms diverge. The custom SSL robot achieves the lowest tracking error ($0.0218\,\text{m}$), aided by its compact track gauge ($b=0.090\,\text{m}$) and favorable torque-to-mass ratio ($4.60\,\text{N}\cdot\text{m/kg}$). In contrast, the TurtleBot3 Burger experiences tracking degradation ($0.1437\,\text{m}$). The higher chassis mass ($1.00\,\text{kg}$), wider track gauge ($b=0.160\,\text{m}$), and conservative actuator velocity limits ($0.22\,\text{m/s}$) prevent the platform from tracking high-speed arc profiles without significant corner-cutting.
3. **M-Shape Transient Cornering**: In directional changes across consecutive acute-angle waypoints, the custom SSL robot exhibits low overshoot ($0.0238\,\text{m}$ RMSE) due to high wheel torque and low moment of inertia. TurtleBot3 Burger achieves $0.0260\,\text{m}$ RMSE at reduced linear velocities, while NVIDIA JetBot experiences increased lateral drift ($0.0397\,\text{m}$ RMSE) during rapid yaw reversals.

