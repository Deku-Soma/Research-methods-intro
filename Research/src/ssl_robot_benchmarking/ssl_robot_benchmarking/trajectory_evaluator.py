#!/usr/bin/env python3
"""
Trajectory Evaluator Node
Evaluates Scenario 2: Trajectory Tracking across:
  - Straight Line
  - Circular Arc
  - M-Shape Course
Calculates Root Mean Square Error (RMSE) path fidelity:
  E_path = sqrt( 1/N * sum( (x_k - x_hat_k)^2 + (y_k - y_hat_k)^2 ) )
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from ssl_robot_interfaces.msg import BenchmarkMetric

class TrajectoryEvaluator(Node):
    def __init__(self):
        super().__init__('trajectory_evaluator')

        self.declare_parameter('scenario_name', 'M-Shape')
        self.scenario_name = self.get_parameter('scenario_name').get_parameter_value().string_value

        self.ref_path = []
        self.actual_poses = []
        self.squared_errors = []

        # Subscriptions
        self.path_sub = self.create_subscription(
            Path,
            '/trajectory/reference_path',
            self.path_callback,
            10
        )

        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/camera_tracking/robot_pose',
            self.pose_callback,
            10
        )

        self.metric_pub = self.create_publisher(BenchmarkMetric, '/benchmark/metrics', 10)

        self.get_logger().info(f"Trajectory Evaluator initialized for '{self.scenario_name}'.")

    def path_callback(self, msg: Path):
        self.ref_path = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]

    def pose_callback(self, msg: PoseStamped):
        if not self.ref_path:
            return

        rx = msg.pose.position.x
        ry = msg.pose.position.y
        self.actual_poses.append((rx, ry))

        # Find closest reference path point
        min_dist_sq = min((rx - px)**2 + (ry - py)**2 for px, py in self.ref_path)
        self.squared_errors.append(min_dist_sq)

    def calculate_rmse(self):
        if not self.squared_errors:
            return 0.0
        return math.sqrt(sum(self.squared_errors) / len(self.squared_errors))

    def publish_metrics(self):
        rmse = self.calculate_rmse()
        self.get_logger().info("=" * 60)
        self.get_logger().info(f"TRAJECTORY EVALUATION [{self.scenario_name}]:")
        self.get_logger().info(f"  Sample count (N): {len(self.squared_errors)}")
        self.get_logger().info(f"  Path RMSE (E_path): {rmse:.4f} meters")
        self.get_logger().info("=" * 60)

        metric = BenchmarkMetric()
        metric.header.stamp = self.get_clock().now().to_msg()
        metric.scenario_name = f"Trajectory: {self.scenario_name}"
        metric.path_rmse = float(rmse)
        metric.passed_ssl_criteria = bool(rmse < 0.15) # Within 15cm tracking envelope
        self.metric_pub.publish(metric)

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryEvaluator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.publish_metrics()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
