#!/usr/bin/env python3
"""
Trial Orchestrator and Statistical Evaluator
Automates 10-iteration benchmarking batches across all scenarios.
Computes mean and sample standard deviation (Metric 7: System Consistency):
  sigma_x = sqrt( 1/(n-1) * sum( (x_j - x_bar)^2 ) )
Exports publication-ready CSV logs and summary comparison plots.
"""

import os
import csv
import math
import numpy as np
import rclpy
from rclpy.node import Node
from ssl_robot_interfaces.msg import BenchmarkMetric

class TrialOrchestrator(Node):
    def __init__(self):
        super().__init__('trial_orchestrator')

        self.declare_parameter('total_trials', 10)
        self.declare_parameter('output_dir', '/ros2_ws/benchmark_results')

        self.total_trials = self.get_parameter('total_trials').get_parameter_value().integer_value
        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_value
        os.makedirs(self.output_dir, exist_ok=True)

        self.records = []
        self.metric_sub = self.create_subscription(
            BenchmarkMetric,
            '/benchmark/metrics',
            self.metric_callback,
            10
        )

        self.get_logger().info(f"Trial Orchestrator listening for {self.total_trials} test trials. Output: {self.output_dir}")

    def metric_callback(self, msg: BenchmarkMetric):
        row = {
            'scenario': msg.scenario_name,
            'trial': len(self.records) + 1,
            'v_max': msg.max_velocity,
            't_stop': msg.stopping_time,
            'd_stop': msg.stopping_distance,
            'path_rmse': msg.path_rmse,
            'latency_ms': msg.command_latency_ms,
            'passed': msg.passed_ssl_criteria
        }
        self.records.append(row)
        self.get_logger().info(f"Recorded Trial {row['trial']}/{self.total_trials} for {row['scenario']}")

        if len(self.records) >= self.total_trials:
            self.compile_and_export_statistics()

    def compile_and_export_statistics(self):
        csv_path = os.path.join(self.output_dir, 'benchmark_metrics_summary.csv')
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)

        self.get_logger().info(f"Saved complete raw trials to {csv_path}")

        # Compute statistical consistency
        v_maxs = [r['v_max'] for r in self.records if r['v_max'] > 0]
        t_stops = [r['t_stop'] for r in self.records if r['t_stop'] > 0]
        d_stops = [r['d_stop'] for r in self.records if r['d_stop'] > 0]

        self.get_logger().info("=" * 60)
        self.get_logger().info(f"SYSTEM CONSISTENCY REPORT (N = {len(self.records)} Trials):")
        if v_maxs:
            mean_v = np.mean(v_maxs)
            std_v = np.std(v_maxs, ddof=1) if len(v_maxs) > 1 else 0.0
            self.get_logger().info(f"  v_max:  mean = {mean_v:.3f} m/s, std dev (sigma) = {std_v:.4f}")
        if t_stops:
            mean_t = np.mean(t_stops)
            std_t = np.std(t_stops, ddof=1) if len(t_stops) > 1 else 0.0
            self.get_logger().info(f"  t_stop: mean = {mean_t:.3f} s,   std dev (sigma) = {std_t:.4f}")
        if d_stops:
            mean_d = np.mean(d_stops)
            std_d = np.std(d_stops, ddof=1) if len(d_stops) > 1 else 0.0
            self.get_logger().info(f"  d_stop: mean = {mean_d:.3f} m,   std dev (sigma) = {std_d:.4f}")
        self.get_logger().info("=" * 60)

def main(args=None):
    rclpy.init(args=args)
    node = TrialOrchestrator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
