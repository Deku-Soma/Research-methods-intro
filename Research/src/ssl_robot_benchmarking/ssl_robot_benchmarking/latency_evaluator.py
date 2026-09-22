#!/usr/bin/env python3
"""
Step-Response Latency Evaluator Node
Evaluates Scenario 3: Step-Response Latency.
Measures delay between command transmission (t_command) and physical motion (t_motion):
  tau_latency = t_motion - t_command
Checks if delay is within the 16.7 ms boundary for 60Hz SSL-Vision frames.
"""

import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from ssl_robot_interfaces.msg import BenchmarkMetric

class LatencyEvaluator(Node):
    def __init__(self):
        super().__init__('latency_evaluator')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.metric_pub = self.create_publisher(BenchmarkMetric, '/benchmark/metrics', 10)

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.state = 'WAITING_FOR_STANDSTILL'
        self.t_command = 0.0
        self.t_motion = 0.0
        self.baseline_acc_x = 0.0
        self.samples_collected = 0

        # Run test sequence after 2.0s settling
        self.timer = self.create_timer(2.0, self.trigger_step_command)
        self.get_logger().info("Latency Evaluator node active. Stabilizing baseline...")

    def imu_callback(self, msg: Imu):
        acc_x = msg.linear_acceleration.x

        if self.state == 'WAITING_FOR_STANDSTILL':
            self.baseline_acc_x = 0.9 * self.baseline_acc_x + 0.1 * acc_x
            self.samples_collected += 1

        elif self.state == 'COMMAND_SENT':
            # Check for sudden physical acceleration departure (> 0.2 m/s^2)
            if abs(acc_x - self.baseline_acc_x) > 0.20:
                self.t_motion = time.time()
                self.state = 'MEASURED'
                self.report_results()

    def trigger_step_command(self):
        if self.state != 'WAITING_FOR_STANDSTILL' or self.samples_collected < 10:
            return

        self.state = 'COMMAND_SENT'
        self.t_command = time.time()

        cmd = Twist()
        cmd.linear.x = 1.0  # Step velocity command
        self.cmd_pub.publish(cmd)
        self.get_logger().info("Step command published to /cmd_vel.")

    def report_results(self):
        latency_ms = (self.t_motion - self.t_command) * 1000.0
        passed = latency_ms <= 16.7

        self.get_logger().info("=" * 60)
        self.get_logger().info("STEP-RESPONSE LATENCY TEST RESULTS:")
        self.get_logger().info(f"  Command Latency (tau_latency): {latency_ms:.2f} ms")
        self.get_logger().info(f"  60Hz SSL-Vision Threshold:    16.70 ms")
        self.get_logger().info(f"  Compliance:                   {'PASSED' if passed else 'FAILED'}")
        self.get_logger().info("=" * 60)

        metric = BenchmarkMetric()
        metric.header.stamp = self.get_clock().now().to_msg()
        metric.scenario_name = "Step-Response Latency"
        metric.command_latency_ms = float(latency_ms)
        metric.passed_ssl_criteria = bool(passed)
        self.metric_pub.publish(metric)

def main(args=None):
    rclpy.init(args=args)
    node = LatencyEvaluator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
