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
import time
import numpy as np
import rclpy
from rclpy.node import Node
from ssl_robot_interfaces.msg import BenchmarkMetric

class TrialOrchestrator(Node):
    def __init__(self):
        super().__init__('trial_orchestrator')

        self.declare_parameter('robot_model', 'ssl_robot')
        self.declare_parameter('total_trials', 10)
        self.declare_parameter('output_dir', '/ros2_ws/benchmark_results')

        self.robot_model = self.get_parameter('robot_model').get_parameter_value().string_value
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

        self.get_logger().info(
            f"Trial Orchestrator listening for {self.total_trials} test trials for robot '{self.robot_model}'. "
            f"Output: {self.output_dir}"
        )

    def metric_callback(self, msg: BenchmarkMetric):
        row = {
            'robot_model': self.robot_model,
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
        self.get_logger().info(f"[{self.robot_model}] Recorded Trial {row['trial']}/{self.total_trials} for {row['scenario']}")
        self.compile_and_export_statistics()
        if len(self.records) >= self.total_trials:
            self.get_logger().info("All benchmark trials recorded. Allowing 2.5s settling pause before shutdown.")
            time.sleep(2.5)
            self.get_logger().info("Initiating clean shutdown.")
            raise SystemExit

    def compile_and_export_statistics(self):
        # 1. Model-specific run CSV
        csv_filename = f"benchmark_metrics_{self.robot_model}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)

        # 2. Append to master comparative CSV
        master_csv_path = os.path.join(self.output_dir, 'benchmark_comparative_master.csv')
        file_exists = os.path.exists(master_csv_path)
        with open(master_csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(self.records)

        self.get_logger().info(f"Saved complete raw trials to {csv_path} and appended to {master_csv_path}")

        # Compute statistical consistency
        v_maxs = [r['v_max'] for r in self.records if r['v_max'] > 0]
        t_stops = [r['t_stop'] for r in self.records if r['t_stop'] > 0]
        d_stops = [r['d_stop'] for r in self.records if r['d_stop'] > 0]
        rmses = [r['path_rmse'] for r in self.records if r['path_rmse'] > 0]
        latencies = [r['latency_ms'] for r in self.records if r['latency_ms'] > 0]

        self.get_logger().info("=" * 65)
        self.get_logger().info(f"SYSTEM CONSISTENCY REPORT - {self.robot_model} (N = {len(self.records)} Trials):")
        if v_maxs:
            mean_v = np.mean(v_maxs)
            std_v = np.std(v_maxs, ddof=1) if len(v_maxs) > 1 else 0.0
            self.get_logger().info(f"  v_max:      mean = {mean_v:.3f} m/s, std dev (sigma) = {std_v:.4f}")
        if t_stops:
            mean_t = np.mean(t_stops)
            std_t = np.std(t_stops, ddof=1) if len(t_stops) > 1 else 0.0
            self.get_logger().info(f"  t_stop:     mean = {mean_t:.3f} s,   std dev (sigma) = {std_t:.4f}")
        if d_stops:
            mean_d = np.mean(d_stops)
            std_d = np.std(d_stops, ddof=1) if len(d_stops) > 1 else 0.0
            self.get_logger().info(f"  d_stop:     mean = {mean_d:.3f} m,   std dev (sigma) = {std_d:.4f}")
        if rmses:
            mean_rmse = np.mean(rmses)
            std_rmse = np.std(rmses, ddof=1) if len(rmses) > 1 else 0.0
            self.get_logger().info(f"  path_rmse:  mean = {mean_rmse:.4f} m, std dev (sigma) = {std_rmse:.4f}")
        if latencies:
            mean_lat = np.mean(latencies)
            std_lat = np.std(latencies, ddof=1) if len(latencies) > 1 else 0.0
            self.get_logger().info(f"  latency:    mean = {mean_lat:.2f} ms, std dev (sigma) = {std_lat:.3f}")
        self.get_logger().info("=" * 65)

def main(args=None):
    rclpy.init(args=args)
    node = TrialOrchestrator()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
