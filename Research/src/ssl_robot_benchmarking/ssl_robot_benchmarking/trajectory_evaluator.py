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

        self.has_published = False
        self.furthest_path_idx = 0
        self.completion_timer = self.create_timer(0.5, self.check_completion)
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

        # Search forward around current waypoint progress
        min_dist_sq = float('inf')
        closest_idx = self.furthest_path_idx
        search_start = max(0, self.furthest_path_idx - 15)
        search_end = min(len(self.ref_path), self.furthest_path_idx + 45)
        for i in range(search_start, search_end):
            d_sq = (rx - self.ref_path[i][0])**2 + (ry - self.ref_path[i][1])**2
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                closest_idx = i

        self.squared_errors.append(min_dist_sq)
        if closest_idx > self.furthest_path_idx:
            self.furthest_path_idx = closest_idx

    def check_completion(self):
        if self.has_published or len(self.squared_errors) < 80 or not self.ref_path:
            return

        rx, ry = self.actual_poses[-1]
        end_x, end_y = self.ref_path[-1]
        dist_to_end = math.hypot(rx - end_x, ry - end_y)

        # Has traversed at least 85% of waypoints along the trajectory
        has_traversed = self.furthest_path_idx >= int(len(self.ref_path) * 0.85)

        # Reached destination after traversing path
        reached_destination = has_traversed and (dist_to_end < 0.30 or self.furthest_path_idx >= len(self.ref_path) - 2)

        # Generous timeout: 60s (3600 samples at 60 Hz) to allow slow baselines to complete full course
        timed_out = len(self.squared_errors) >= 3600

        if reached_destination or timed_out:
            self.has_published = True
            self.publish_metrics()

    def calculate_rmse(self):
        if not self.squared_errors:
            return 0.0
        return math.sqrt(sum(self.squared_errors) / len(self.squared_errors))

    def publish_metrics(self):
        if not rclpy.ok():
            return
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
    except (KeyboardInterrupt, SystemExit):
        if not node.has_published:
            node.publish_metrics()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
