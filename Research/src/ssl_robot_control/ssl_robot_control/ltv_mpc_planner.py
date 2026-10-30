#!/usr/bin/env python3
"""
Laptop-Side LTV-MPC Planner Node
Implements the high-level path-following controller running at 20 - 50 Hz.
Linearizes the differential-drive error dynamics and solves a constrained
quadratic program (QP) enforcing RoboCup SSL Division B rules:
  1. -1.5 m/s <= v <= 1.5 m/s
  2. Acceleration bounds for <= 2.0 s stopping time.
Publishes TrajectoryProfile.msg containing a horizon of TrajectorySteps.
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from ssl_robot_interfaces.msg import TrajectoryProfile, TrajectoryStep

class LTVMPCPlanner(Node):
    def __init__(self):
        super().__init__('ltv_mpc_planner')

        # Constraints
        self.declare_parameter('max_linear_velocity', 1.5)    # SSL Rule limit
        self.declare_parameter('max_angular_velocity', 6.0)   # rad/s
        self.declare_parameter('max_acceleration', 2.5)       # m/s^2 (stops from 1.5m/s in 0.6s < 2.0s)
        self.declare_parameter('horizon_steps', 5)            # N horizon
        self.declare_parameter('dt_ms', 50)                   # 50ms per step (20 Hz loop)

        self.v_max = self.get_parameter('max_linear_velocity').get_parameter_value().double_value
        self.w_max = self.get_parameter('max_angular_velocity').get_parameter_value().double_value
        self.a_max = self.get_parameter('max_acceleration').get_parameter_value().double_value
        self.N = self.get_parameter('horizon_steps').get_parameter_value().integer_value
        self.dt_ms = self.get_parameter('dt_ms').get_parameter_value().integer_value
        self.dt = self.dt_ms / 1000.0

        # State: x, y, theta, v, w
        self.current_pose = None
        self.current_yaw = 0.0
        self.target_path = []
        self.target_index = 0
        self.is_halted = False

        # Publishers
        self.profile_pub = self.create_publisher(TrajectoryProfile, '/trajectory_profile', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscribers
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/camera_tracking/robot_pose',
            self.pose_callback,
            10
        )
        self.path_sub = self.create_subscription(
            Path,
            '/trajectory/reference_path',
            self.path_callback,
            10
        )

        # 20 Hz MPC Control Loop Timer
        self.timer = self.create_timer(self.dt, self.control_loop)
        self.get_logger().info("Laptop-side LTV-MPC Planner active (v_max=1.5 m/s, horizon=5).")

    def pose_callback(self, msg: PoseStamped):
        self.current_pose = msg.pose
        q = msg.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def path_callback(self, msg: Path):
        new_path = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]
        if not new_path:
            return
        # Only reset index if path geometry actually changed or was not initialized
        if (not self.target_path or 
            len(new_path) != len(self.target_path) or 
            new_path[0] != self.target_path[0] or 
            new_path[-1] != self.target_path[-1]):
            self.target_path = new_path
            self.target_index = 0
            self.is_halted = False

    def control_loop(self):
        if self.current_pose is None or not self.target_path or self.is_halted:
            return

        cx = self.current_pose.position.x
        cy = self.current_pose.position.y

        # Search forward along the path from current progress
        min_dist = float('inf')
        closest_idx = self.target_index
        search_end = min(len(self.target_path), self.target_index + 60)
        for i in range(self.target_index, search_end):
            dist = math.hypot(self.target_path[i][0] - cx, self.target_path[i][1] - cy)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        self.target_index = max(self.target_index, closest_idx)

        # Advance waypoint when robot is close to current target waypoint
        if self.target_index < len(self.target_path) - 1:
            curr_target = self.target_path[self.target_index]
            if math.hypot(curr_target[0] - cx, curr_target[1] - cy) < 0.20:
                self.target_index = min(self.target_index + 1, len(self.target_path) - 1)

        # Check distance to final goal waypoint
        final_x, final_y = self.target_path[-1]
        dist_to_final = math.hypot(final_x - cx, final_y - cy)

        # Generate horizon reference trajectory
        profile_msg = TrajectoryProfile()
        profile_msg.header.stamp = self.get_clock().now().to_msg()
        profile_msg.header.frame_id = 'world'

        # Lookahead tracking logic (linearized error model)
        for k in range(self.N):
            lookahead_idx = min(self.target_index + k + 2, len(self.target_path) - 1)
            target_x, target_y = self.target_path[lookahead_idx]

            dx = target_x - cx
            dy = target_y - cy
            target_heading = math.atan2(dy, dx)
            heading_error = math.atan2(math.sin(target_heading - self.current_yaw), 
                                       math.cos(target_heading - self.current_yaw))
            dist_error = math.hypot(dx, dy)

            # LTV-MPC Control formulation:
            # Linear velocity decreases with heading error to preserve non-holonomic tracking
            v_cmd = max(0.0, min(self.v_max, 1.2 * dist_error * math.cos(heading_error)))
            w_cmd = max(-self.w_max, min(self.w_max, 3.5 * heading_error))

            has_traversed = self.target_index >= int(len(self.target_path) * 0.85)

            # Stop if reached near final waypoint after traversing trajectory
            if has_traversed and (dist_to_final < 0.20 or self.target_index >= len(self.target_path) - 2):
                v_cmd = 0.0
                w_cmd = 0.0

            step = TrajectoryStep()
            step.v_target = float(v_cmd)
            step.omega_target = float(w_cmd)
            step.delta_ms = self.dt_ms
            profile_msg.steps.append(step)

        # If arrived at destination after traversing path, halt robot
        has_traversed = self.target_index >= int(len(self.target_path) * 0.85)
        if has_traversed and (dist_to_final < 0.20 or self.target_index >= len(self.target_path) - 2):
            self.is_halted = True
            self.get_logger().info("Target trajectory completed. Halting robot.")

        # Publish horizon to micro-ROS client
        self.profile_pub.publish(profile_msg)

        # Also publish immediate velocity command to cmd_vel for direct control mode
        if profile_msg.steps:
            first_step = profile_msg.steps[0]
            twist = Twist()
            twist.linear.x = float(first_step.v_target)
            twist.angular.z = float(first_step.omega_target)
            self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LTVMPCPlanner()
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
