#!/usr/bin/env python3
"""
Sprint and Halt Evaluator Node
Evaluates Scenario 1: Straight-Line Sprint and Halt.
Measures:
  1. Maximum Velocity (v_max <= 1.5 m/s)
  2. Stopping Time (t_stop <= 2.0 s)
  3. Stopping Distance (d_stop)
Publishes BenchmarkMetric.msg and logs data.
"""

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
        self.declare_parameter('target_velocity', 1.4)    # Target sprint speed
        self.declare_parameter('start_x', 0.0)

        self.sprint_dist = self.get_parameter('sprint_distance').get_parameter_value().double_value
        self.v_target = self.get_parameter('target_velocity').get_parameter_value().double_value
        self.start_x = self.get_parameter('start_x').get_parameter_value().double_value

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
        self.halt_pos = None
        self.stop_pos = None

        self.max_velocity = 0.0
        self.t_start = 0.0
        self.t_halt = 0.0
        self.t_zero = 0.0

        self.timer = self.create_timer(0.02, self.evaluation_loop)
        self.get_logger().info("Sprint and Halt Evaluator initialized.")

    def odom_callback(self, msg: Odometry):
        pos = msg.pose.pose.position
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        current_speed = math.hypot(vx, vy)

        if current_speed > self.max_velocity:
            self.max_velocity = current_speed

        if self.state == 'INIT':
            self.initial_pos = (pos.x, pos.y)
            self.t_start = time.time()
            self.state = 'SPRINTING'
            self.get_logger().info("Sprint test started! Accelerating forward...")

        elif self.state == 'SPRINTING':
            dist_traveled = pos.x - self.initial_pos[0]
            if dist_traveled >= self.sprint_dist:
                self.t_halt = time.time()
                self.halt_pos = (pos.x, pos.y)
                self.state = 'HALTED'
                self.get_logger().info(f"Crossed 5.0m sprint line! Broadcasting HALT command at v = {current_speed:.2f} m/s.")

        elif self.state == 'HALTED':
            if current_speed < 0.01:
                self.t_zero = time.time()
                self.stop_pos = (pos.x, pos.y)
                self.state = 'FINISHED'
                self.record_results()

    def evaluation_loop(self):
        cmd = Twist()
        if self.state == 'SPRINTING':
            cmd.linear.x = self.v_target
            self.cmd_pub.publish(cmd)
        elif self.state == 'HALTED':
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

    def record_results(self):
        t_stop = self.t_zero - self.t_halt
        d_stop = math.hypot(self.stop_pos[0] - self.halt_pos[0], self.stop_pos[1] - self.halt_pos[1])
        v_max = self.max_velocity

        passed = (v_max <= 1.50) and (t_stop <= 2.0)

        self.get_logger().info("=" * 60)
        self.get_logger().info("SPRINT & HALT TEST RESULTS:")
        self.get_logger().info(f"  Maximum Velocity (v_max): {v_max:.3f} m/s (Rule: <= 1.5 m/s)")
        self.get_logger().info(f"  Stopping Time (t_stop):    {t_stop:.3f} s   (Rule: <= 2.0 s)")
        self.get_logger().info(f"  Stopping Distance (d_stop):{d_stop:.3f} m")
        self.get_logger().info(f"  SSL Rule Compliance:       {'PASSED' if passed else 'FAILED'}")
        self.get_logger().info("=" * 60)

        metric = BenchmarkMetric()
        metric.header.stamp = self.get_clock().now().to_msg()
        metric.scenario_name = "Sprint and Halt"
        metric.trial_number = 1
        metric.max_velocity = float(v_max)
        metric.stopping_time = float(t_stop)
        metric.stopping_distance = float(d_stop)
        metric.passed_ssl_criteria = bool(passed)
        metric.notes = f"Target {self.v_target} m/s over {self.sprint_dist} m"
        self.metric_pub.publish(metric)

def main(args=None):
    rclpy.init(args=args)
    node = SprintHaltEvaluator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
