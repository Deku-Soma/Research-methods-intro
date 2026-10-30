#!/usr/bin/env python3
"""
Simulated Raspberry Pi Pico Firmware Node
Emulates the dual-core architecture of the RP2040 microcontroller:
  - Core 0: micro-ROS communication client, trajectory buffer queue.
  - Core 1: High-frequency (200-500 Hz) PID wheel velocity control,
            inverse differential kinematics, and MPU6050 complementary filter.
"""

import math
import collections
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, JointState
from ssl_robot_interfaces.msg import TrajectoryProfile, TrajectoryStep

class SimulatedPicoFirmware(Node):
    def __init__(self):
        super().__init__('simulated_pico_firmware')

        # Kinematic parameters and baseline support
        self.declare_parameter('robot_model', 'ssl_robot')
        self.declare_parameter('wheel_radius', 0.025)       # 25mm radius for custom SSL robot
        self.declare_parameter('wheel_separation', 0.090)   # 90mm track width for custom SSL robot

        self.robot_model = self.get_parameter('robot_model').get_parameter_value().string_value
        self.wheel_radius = self.get_parameter('wheel_radius').get_parameter_value().double_value
        self.wheel_separation = self.get_parameter('wheel_separation').get_parameter_value().double_value

        # High-frequency loop parameter (Core 1 frequency)
        self.declare_parameter('control_rate_hz', 200.0) # 200 Hz
        self.declare_parameter('kp', 1.8)
        self.declare_parameter('ki', 0.1)
        self.declare_parameter('kd', 0.05)
        self.declare_parameter('filter_alpha', 0.98)     # Complementary filter weight

        rate = self.get_parameter('control_rate_hz').get_parameter_value().double_value
        self.dt = 1.0 / rate

        self.kp = self.get_parameter('kp').get_parameter_value().double_value
        self.ki = self.get_parameter('ki').get_parameter_value().double_value
        self.kd = self.get_parameter('kd').get_parameter_value().double_value
        self.alpha = self.get_parameter('filter_alpha').get_parameter_value().double_value

        # Best-Effort QoS matching micro-ROS policy in proposal
        best_effort_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        # Core 0: Trajectory horizon buffer queue
        self.trajectory_buffer = collections.deque(maxlen=10)

        # State tracking (Core 1)
        self.measured_left_vel = 0.0
        self.measured_right_vel = 0.0
        self.target_left_vel = 0.0
        self.target_right_vel = 0.0

        # PID state
        self.err_left_integral = 0.0
        self.err_left_prev = 0.0
        self.err_right_integral = 0.0
        self.err_right_prev = 0.0

        # Complementary filter state (heading fusion)
        self.fused_heading = 0.0
        self.last_gyro_z = 0.0

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscribers
        self.profile_sub = self.create_subscription(
            TrajectoryProfile,
            '/trajectory_profile',
            self.core0_profile_callback,
            best_effort_qos
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.core1_imu_callback,
            10
        )

        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.core1_joint_callback,
            10
        )

        # Core 1 200 Hz Execution Timer
        self.timer = self.create_timer(self.dt, self.core1_control_loop)
        self.get_logger().info(f"Simulated Pico Dual-Core Firmware started (Core 1 @ {rate} Hz).")

    # =========================================================================
    # CORE 0: micro-ROS Communication and Buffer
    # =========================================================================
    def core0_profile_callback(self, msg: TrajectoryProfile):
        """Buffers incoming trajectory steps from the laptop MPC node."""
        self.trajectory_buffer.clear()
        for step in msg.steps:
            self.trajectory_buffer.append(step)

    # =========================================================================
    # CORE 1: High-Frequency Sensor Fusion & Discrete PID Loop
    # =========================================================================
    def core1_joint_callback(self, msg: JointState):
        """Reads quadrature wheel encoders."""
        for i, name in enumerate(msg.name):
            if name == 'left_wheel_joint' and i < len(msg.velocity):
                self.measured_left_vel = msg.velocity[i]
            elif name == 'right_wheel_joint' and i < len(msg.velocity):
                self.measured_right_vel = msg.velocity[i]

    def core1_imu_callback(self, msg: Imu):
        """MPU6050 Complementary Filter: theta_fused = alpha*(theta + gyro*dt) + (1-alpha)*accel"""
        self.last_gyro_z = msg.angular_velocity.z
        acc_x = msg.linear_acceleration.x
        acc_y = msg.linear_acceleration.y
        acc_heading = math.atan2(acc_y, acc_x) if (abs(acc_x) > 0.01 or abs(acc_y) > 0.01) else self.fused_heading

        self.fused_heading = self.alpha * (self.fused_heading + self.last_gyro_z * self.dt) + (1.0 - self.alpha) * acc_heading

    def core1_control_loop(self):
        """Executes inverse kinematics and wheel PID velocity control."""
        if not self.trajectory_buffer:
            return

        # Pop or inspect active trajectory step
        active_step = self.trajectory_buffer[0]
        v = active_step.v_target
        w = active_step.omega_target

        # Inverse Differential Kinematics
        # phi_dot_L = (v - w * L / 2) / R
        # phi_dot_R = (v + w * L / 2) / R
        target_phi_l = (v - w * self.wheel_separation / 2.0) / self.wheel_radius
        target_phi_r = (v + w * self.wheel_separation / 2.0) / self.wheel_radius

        # Discrete PID: Left Motor
        err_l = target_phi_l - self.measured_left_vel
        self.err_left_integral += err_l * self.dt
        deriv_l = (err_l - self.err_left_prev) / self.dt if self.dt > 0 else 0.0
        self.err_left_prev = err_l
        u_l = (self.kp * err_l) + (self.ki * self.err_left_integral) + (self.kd * deriv_l)

        # Discrete PID: Right Motor
        err_r = target_phi_r - self.measured_right_vel
        self.err_right_integral += err_r * self.dt
        deriv_r = (err_r - self.err_right_prev) / self.dt if self.dt > 0 else 0.0
        self.err_right_prev = err_r
        u_r = (self.kp * err_r) + (self.ki * self.err_right_integral) + (self.kd * deriv_r)

        # Forward Kinematics to /cmd_vel for Gazebo actuation
        effective_v = (target_phi_r + target_phi_l) * self.wheel_radius / 2.0
        effective_w = (target_phi_r - target_phi_l) * self.wheel_radius / self.wheel_separation

        cmd = Twist()
        cmd.linear.x = float(effective_v)
        cmd.angular.z = float(effective_w)
        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SimulatedPicoFirmware()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
