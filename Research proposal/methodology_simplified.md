# Simplified Methodology for Re-evaluation

This document presents the proposed methodology section in plain, straightforward language. It integrates the corrections for the advisor's comments to help evaluate the design before updating the main LaTeX document.

---

## 1. Hardware Design and Components

### The Robot Body (Chassis)
* **Shape**: A simple cylinder, 10 cm wide and 10 cm high. Symmetrical shapes are easier to 3D print and rotate smoothly in tight spaces.
* **Base Plate**: Has three cutouts: two for the main driving wheels and one for a passive caster wheel at the back to keep the robot balanced.
* **Cover**: An open-top 3D-printed cover that mounts directly to the base. The open top allows air to cool the electronics and makes it easy to reach motor wires.
* **Assembly**: All wire connections are soldered to prevent short circuits and loose connections during fast movements.

### Key Electronic Components
* **Microcontroller**: A Raspberry Pi Pico board (51 mm by 21 mm). It is cheap, small, and runs micro-ROS, which allows it to send and receive data from the main computer.
* **Motors**: Two spur gear DC motors. These are inexpensive, common, and have built-in gearboxes to provide high turning force (torque) at lower speeds.
* **Wheel Encoders**: Sensors attached to the motors that count wheel rotations. These are used for local speed control.
* **IMU (Inertial Measurement Unit)**: An MPU6050 sensor that measures linear acceleration and turning speed (yaw rate). It is mounted near the center of the robot.

---

## 2. Software and Communication Stack

### How the Systems Talk (ROS 2 and micro-ROS)
* **The Main Computer**: A laptop runs the high-level ROS 2 nodes responsible for path planning and navigation.
* **The Robot**: The Raspberry Pi Pico runs a micro-ROS client node to control the motors directly.
* **The Bridge**: A micro-ROS Agent running on the laptop bridges communication between the Pico and the main ROS 2 network over Wi-Fi.
* **The Loop**:
  1. The laptop calculates the desired speed and sends velocity commands to the Pico.
  2. The Pico receives these commands and adjusts the motor speeds using the wheel encoders for feedback.
  3. The Pico sends acceleration and orientation data from the MPU6050 sensor back to the laptop.

### Tracking System (Localization)
* **Camera**: An overhead camera views the playing field.
* **Marker**: A unique paper pattern (sigil) is glued to the top of the robot.
* **Processing**: The laptop processes the video feed to track the robot's coordinates and heading in real time.

### Motor Speed Control (PID Loop)
* The Pico runs a Proportional-Integral-Derivative (PID) controller to keep the wheels spinning at the target speed.
* **Feedback Source**: The PID controller reads the wheel encoders (not the accelerometer) to calculate the error between target wheel speed and actual wheel speed. It adjusts the motor power (PWM signals) to minimize this error.

---

## 3. Benchmarking and Testing Protocols

We will compare our custom 3D-printed robot against two commercial baselines: the TurtleBot (a standard research robot) and the NVIDIA JetBot (a low-cost differential drive robot).

### Test Scenarios
1. **Sprint and Stop**: The robot drives forward in a straight line for 5 meters at top speed, and then stops immediately when it receives a halt command.
2. **Path Following**: The robot follows three different path shapes to test how well it steers:
   * *Straight Line*: Tests if the robot drifts to the side.
   * *Circle*: Tests constant turning.
   * *M-Shape*: Tests sharp corners, quick stops, and rapid direction changes.
3. **Latency Test**: The robot stands still, receives a start command, and we measure the delay before the wheels physically begin to move.

### Performance Metrics
* **Top Speed ($v_{\text{max}}$)**: The fastest speed the robot achieves during the 5-meter sprint. (RoboCup rules limit this to 1.5 m/s).
* **Stopping Time ($t_{\text{stop}}$)**: How many seconds it takes the robot to come to a complete stop after a halt command is sent. (RoboCup rules allow a maximum of 2.0 seconds).
* **Stopping Distance ($d_{\text{stop}}$)**: The physical distance the robot travels after the halt command is issued.
* **Path Error ($E_{\text{path}}$)**: The average distance (RMSE) between where the robot was supposed to drive and where it actually drove, measured by the overhead camera.
* **Turning Radius ($R_{\text{turn}}$)**: The minimum circle size the robot can draw on the ground when turning.
* **Command Latency ($\tau_{\text{latency}}$)**: The time delay between sending a command from the laptop and the robot's accelerometer registering movement.
* **Consistency ($\sigma_x$)**: We run each test 10 times and calculate the standard deviation to see how predictable the robot's behavior is.

---

## 4. Operational Safety and Calibration Controls

To ensure our tests are fair and reproducible, we implement these procedures:
* **Camera Calibration**: Calculate a translation grid (homography matrix) to convert camera pixels into physical millimeter coordinates on the field.
* **Time Sync**: Synchronize the internal clocks of the Pico and the laptop using the micro-ROS time service to ensure latency measurements are accurate.
* **Data Logging**: Record all commands and sensor data into ROS bag files on the laptop during each run for later analysis.
* **Battery Control**: Monitor battery voltage and only run tests when the battery is above a set charge level. This ensures the motors always have consistent power.
* **Surface Control**: Perform all tests on the same flat carpet surface to keep wheel friction constant.
