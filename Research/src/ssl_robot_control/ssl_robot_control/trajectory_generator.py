#!/usr/bin/env python3
"""
Trajectory Generator Node
Generates reference trajectories for the 3 benchmarking scenarios:
1. Straight-Line 5m Sprint & Halt
2. Circular Arc (steady-state radius tracking)
3. M-Shape Path (transient cornering & rapid acceleration/deceleration)
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import String

class TrajectoryGenerator(Node):
    def __init__(self):
        super().__init__('trajectory_generator')

        self.declare_parameter('scenario', 'straight_line') # 'straight_line', 'circular_arc', 'm_shape'
        self.declare_parameter('target_velocity', 1.2)      # m/s (SSL limit: 1.5 m/s)
        self.declare_parameter('path_resolution', 0.05)     # 5cm waypoint spacing

        self.scenario = self.get_parameter('scenario').get_parameter_value().string_value
        self.v_target = self.get_parameter('target_velocity').get_parameter_value().double_value
        self.resolution = self.get_parameter('path_resolution').get_parameter_value().double_value

        self.path_pub = self.create_publisher(Path, '/trajectory/reference_path', 10)
        self.ref_pose_pub = self.create_publisher(PoseStamped, '/trajectory/target_pose', 10)

        # Scenario command subscriber (allows dynamically changing test scenario)
        self.cmd_sub = self.create_subscription(
            String,
            '/trajectory/set_scenario',
            self.scenario_callback,
            10
        )

        self.waypoints = []
        self.current_index = 0
        self.generate_trajectory()

        # Publish target waypoint at 50 Hz and reference path at 1 Hz
        self.timer = self.create_timer(0.02, self.timer_callback)
        self.path_timer = self.create_timer(1.0, self.path_timer_callback)
        self.get_logger().info(f"Trajectory Generator started with scenario: '{self.scenario}'")

    def path_timer_callback(self):
        if hasattr(self, 'path_msg') and self.path_msg.poses:
            self.path_msg.header.stamp = self.get_clock().now().to_msg()
            self.path_pub.publish(self.path_msg)

    def scenario_callback(self, msg: String):
        req = msg.data.strip()
        if req in ['straight_line', 'circular_arc', 'm_shape']:
            self.scenario = req
            self.current_index = 0
            self.generate_trajectory()
            self.get_logger().info(f"Switched scenario to: '{self.scenario}'")

    def generate_trajectory(self):
        self.waypoints = []
        if self.scenario == 'straight_line':
            # 5-meter sprint lane starting at (0, -2.0) to (5.0, -2.0)
            xs = np.arange(0.0, 5.05, self.resolution)
            for x in xs:
                self.waypoints.append((float(x), -2.0, 0.0, self.v_target))

        elif self.scenario == 'circular_arc':
            # Circle centered at (0.0, 0.0) with radius R = 1.0 m
            radius = 1.0
            thetas = np.arange(0.0, 2 * math.pi, 0.05)
            for th in thetas:
                x = radius * math.cos(th)
                y = radius * math.sin(th)
                heading = th + math.pi / 2.0
                self.waypoints.append((float(x), float(y), float(heading), self.v_target))

        elif self.scenario == 'm_shape':
            # M-Shape key points: (0, 1) -> (1, 3) -> (2, 1.5) -> (3, 3) -> (4, 1)
            keypoints = [
                (0.0, 1.0),
                (1.0, 3.0),
                (2.0, 1.5),
                (3.0, 3.0),
                (4.0, 1.0)
            ]
            for i in range(len(keypoints) - 1):
                p_start = keypoints[i]
                p_end = keypoints[i + 1]
                dx = p_end[0] - p_start[0]
                dy = p_end[1] - p_start[1]
                dist = math.hypot(dx, dy)
                heading = math.atan2(dy, dx)
                steps = max(int(dist / self.resolution), 1)
                for s in range(steps):
                    t = s / steps
                    wx = p_start[0] + t * dx
                    wy = p_start[1] + t * dy
                    self.waypoints.append((float(wx), float(wy), float(heading), self.v_target))

        # Publish the full path message
        self.path_msg = Path()
        self.path_msg.header.stamp = self.get_clock().now().to_msg()
        self.path_msg.header.frame_id = 'world'
        for wp in self.waypoints:
            p = PoseStamped()
            p.header.frame_id = 'world'
            p.pose.position.x = wp[0]
            p.pose.position.y = wp[1]
            p.pose.position.z = 0.025
            self.path_msg.poses.append(p)
        self.path_pub.publish(self.path_msg)

    def timer_callback(self):
        if not self.waypoints:
            return

        wp = self.waypoints[min(self.current_index, len(self.waypoints) - 1)]
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'world'
        pose.pose.position.x = wp[0]
        pose.pose.position.y = wp[1]
        pose.pose.position.z = 0.025
        # Quaternion for yaw
        yaw = wp[2]
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.ref_pose_pub.publish(pose)

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryGenerator()
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
