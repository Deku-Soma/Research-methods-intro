#!/usr/bin/env python3
"""
Sprint and Halt Evaluator Node
Evaluates Scenario 1: Straight-Line Sprint and Halt.
Measures:
  1. Maximum Velocity (v_max <= 1.5 m/s for SSL Stop rule, or unconstrained)
  2. Stopping Time (t_stop <= 2.0 s)
  3. Stopping Distance (d_stop)
Publishes BenchmarkMetric.msg, logs real-time telemetry, and exports to CSV.
"""

import os
import csv
import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from ssl_robot_interfaces.msg import BenchmarkMetric

class SprintHaltEvaluator(Node):
    def __init__(self):
        super().__init__('sprint_halt_evaluator')

        self.declare_parameter('sprint_distance', 5.0)    # 5 meters
        self.declare_parameter('target_velocity', 1.5)    # Target sprint speed
        self.declare_parameter('start_x', 0.0)
        self.declare_parameter('unconstrained', False)
        self.declare_parameter('robot_model', 'ssl_robot')

        self.sprint_dist = self.get_parameter('sprint_distance').get_parameter_value().double_value
        self.v_target = self.get_parameter('target_velocity').get_parameter_value().double_value
        self.start_x = self.get_parameter('start_x').get_parameter_value().double_value
        self.unconstrained = self.get_parameter('unconstrained').get_parameter_value().bool_value
        self.robot_model = self.get_parameter('robot_model').get_parameter_value().string_value

        if self.unconstrained:
            if self.robot_model == 'turtlebot3_burger':
                self.v_target = 0.30
            elif self.robot_model == 'jetbot':
                self.v_target = 0.50
            else:
                self.v_target = 2.00
            self.sprint_dist = 5.0

        # Publishers & Subscribers
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.metric_pub = self.create_publisher(BenchmarkMetric, '/benchmark/metrics', 10)

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # State tracking
        self.state = 'INIT' # INIT -> SPRINTING -> HALTED -> FINISHED
        self.initial_pos = None
        self.initial_yaw = 0.0
        self.current_pos = None
        self.current_yaw = 0.0
        self.current_cmd_v = 0.0
        self.halt_pos = None
        self.stop_pos = None

        self.max_velocity = 0.0
        self.t_start = 0.0
        self.t_halt = 0.0
        self.t_zero = 0.0
        self._last_log_time = 0.0

        self.timer = self.create_timer(0.02, self.evaluation_loop)
        mode_str = "UNCONSTRAINED TOP SPEED" if self.unconstrained else "STANDARD SPRINT & HALT"
        self.get_logger().info(f"Sprint Evaluator initialized [{mode_str}]: Target {self.v_target:.2f} m/s over {self.sprint_dist:.1f} m for {self.robot_model}.")

    def odom_callback(self, msg: Odometry):
        pos = msg.pose.pose.position
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        current_speed = math.hypot(vx, vy)

        # Orientation extraction
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        current_yaw = math.atan2(siny_cosp, cosy_cosp)

        self.current_pos = (pos.x, pos.y)
        self.current_yaw = current_yaw

        if current_speed > self.max_velocity:
            self.max_velocity = current_speed

        now = time.time()

        if self.state == 'INIT':
            self.initial_pos = (pos.x, pos.y)
            self.initial_yaw = current_yaw
            self.t_start = now
            self._last_log_time = now
            self.state = 'SPRINTING'
            self.get_logger().info("Sprint test started! Accelerating forward...")

        elif self.state == 'SPRINTING':
            dist_traveled = math.hypot(pos.x - self.initial_pos[0], pos.y - self.initial_pos[1])

            # Live telemetry logging every 0.5s
            if now - self._last_log_time >= 0.5:
                self._last_log_time = now
                elapsed = now - self.t_start
                self.get_logger().info(
                    f"[Telemetry] Distance: {dist_traveled:5.2f}/{self.sprint_dist:.1f} m | Speed: {current_speed:4.2f} m/s | Peak: {self.max_velocity:4.2f} m/s | Time: {elapsed:4.1f} s"
                )

            if dist_traveled >= self.sprint_dist or (now - self.t_start > 15.0):
                self.t_halt = now
                self.halt_pos = (pos.x, pos.y)
                self.state = 'HALTED'
                self.get_logger().info(f"Reached {self.sprint_dist:.1f}m boundary! Issuing HALT brake command at v = {current_speed:.2f} m/s.")

        elif self.state == 'HALTED':
            if current_speed < 0.03 or (now - self.t_halt > 3.0):
                self.t_zero = now
                self.stop_pos = (pos.x, pos.y)
                self.state = 'FINISHED'
                self.record_results()

    def evaluation_loop(self):
        cmd = Twist()
        dt = 0.02
        if self.state == 'SPRINTING':
            # Smooth acceleration ramping up to max platform torque
            max_accel = 3.0 if self.unconstrained else 2.5
            self.current_cmd_v = min(self.v_target, self.current_cmd_v + max_accel * dt)
            cmd.linear.x = float(self.current_cmd_v)

            # Active heading hold and lateral drift correction
            yaw_error = self.current_yaw - self.initial_yaw
            yaw_error = math.atan2(math.sin(yaw_error), math.cos(yaw_error))

            lateral_drift = 0.0
            if self.current_pos and self.initial_pos:
                dx = self.current_pos[0] - self.initial_pos[0]
                dy = self.current_pos[1] - self.initial_pos[1]
                lateral_drift = dy * math.cos(self.initial_yaw) - dx * math.sin(self.initial_yaw)

            kp_yaw = 2.5
            kp_lat = 1.0
            cmd.angular.z = float(-kp_yaw * yaw_error - kp_lat * lateral_drift)
            self.cmd_pub.publish(cmd)
        elif self.state == 'HALTED':
            self.current_cmd_v = 0.0
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

    def record_results(self):
        t_stop = self.t_zero - self.t_halt
        d_stop = math.hypot(self.stop_pos[0] - self.halt_pos[0], self.stop_pos[1] - self.halt_pos[1])
        v_max = self.max_velocity

        passed = (v_max <= 1.50) and (t_stop <= 2.0) if not self.unconstrained else True

        self.get_logger().info("=" * 60)
        self.get_logger().info(f"SPRINT & HALT TEST RESULTS ({self.robot_model}):")
        self.get_logger().info(f"  Maximum Velocity (v_max): {v_max:.3f} m/s")
        self.get_logger().info(f"  Stopping Time (t_stop):    {t_stop:.3f} s")
        self.get_logger().info(f"  Stopping Distance (d_stop):{d_stop:.3f} m")
        self.get_logger().info(f"  Compliance Status:         {'PASSED' if passed else 'FAILED'}")
        self.get_logger().info("=" * 60)

        metric = BenchmarkMetric()
        metric.header.stamp = self.get_clock().now().to_msg()
        metric.scenario_name = "Sprint and Halt" if not self.unconstrained else "Unconstrained Speed Test"
        metric.trial_number = 1
        metric.max_velocity = float(v_max)
        metric.stopping_time = float(t_stop)
        metric.stopping_distance = float(d_stop)
        metric.passed_ssl_criteria = bool(passed)
        metric.notes = f"Target {self.v_target} m/s over {self.sprint_dist} m"
        self.metric_pub.publish(metric)

        # Write to master CSV
        try:
            output_dir = '/ros2_ws/benchmark_results'
            os.makedirs(output_dir, exist_ok=True)
            master_csv = os.path.join(output_dir, 'benchmark_comparative_master.csv')
            file_exists = os.path.exists(master_csv)
            row = {
                'robot_model': self.robot_model,
                'scenario': metric.scenario_name,
                'trial': 1,
                'v_max': round(float(v_max), 4),
                't_stop': round(float(t_stop), 4),
                'd_stop': round(float(d_stop), 4),
                'path_rmse': 0.0,
                'latency_ms': 0.0,
                'passed': passed
            }
            with open(master_csv, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            self.get_logger().info(f"Logged results directly to {master_csv}")
        except Exception as e:
            self.get_logger().warn(f"Failed to write CSV: {e}")

        # Signal completion
        self.get_logger().info("Test execution completed successfully.")
        raise SystemExit

def main(args=None):
    rclpy.init(args=args)
    node = SprintHaltEvaluator()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
