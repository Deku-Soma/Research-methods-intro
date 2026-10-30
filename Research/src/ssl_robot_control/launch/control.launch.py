from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    robot_model = LaunchConfiguration('robot_model', default='ssl_robot')
    scenario = LaunchConfiguration('scenario', default='straight_line')
    target_vel = LaunchConfiguration('target_velocity', default='1.2')
    tracking_mode = LaunchConfiguration('tracking_mode', default='idealized_ground_truth')

    # Kinematic and dynamic constraints per robot model
    wheel_radius = PythonExpression([
        "0.033 if '", robot_model, "' == 'turtlebot3_burger' else (",
        "0.0325 if '", robot_model, "' == 'jetbot' else 0.025)"
    ])
    wheel_separation = PythonExpression([
        "0.160 if '", robot_model, "' == 'turtlebot3_burger' else (",
        "0.110 if '", robot_model, "' == 'jetbot' else 0.090)"
    ])
    max_linear_velocity = PythonExpression([
        "0.22 if '", robot_model, "' == 'turtlebot3_burger' else (",
        "0.35 if '", robot_model, "' == 'jetbot' else 1.5)"
    ])

    # 1. Overhead Tracking Node (60 Hz SSL-Vision simulation)
    overhead_tracking_node = Node(
        package='ssl_robot_control',
        executable='overhead_tracking_node',
        name='overhead_tracking_node',
        output='screen',
        parameters=[{
            'mode': tracking_mode,
            'noise_std_dev': 0.001,
            'update_rate_hz': 60.0
        }]
    )

    # 2. Trajectory Generator
    trajectory_generator_node = Node(
        package='ssl_robot_control',
        executable='trajectory_generator',
        name='trajectory_generator',
        output='screen',
        parameters=[{
            'scenario': scenario,
            'target_velocity': target_vel,
            'path_resolution': 0.05
        }]
    )

    # 3. Laptop-Side LTV-MPC Planner
    ltv_mpc_planner_node = Node(
        package='ssl_robot_control',
        executable='ltv_mpc_planner',
        name='ltv_mpc_planner',
        output='screen',
        parameters=[{
            'max_linear_velocity': max_linear_velocity,
            'max_angular_velocity': 6.0,
            'max_acceleration': 2.5,
            'horizon_steps': 5,
            'dt_ms': 50
        }]
    )

    # 4. Simulated Pico Dual-Core Firmware
    simulated_pico_node = Node(
        package='ssl_robot_control',
        executable='simulated_pico_firmware',
        name='simulated_pico_firmware',
        output='screen',
        parameters=[{
            'robot_model': robot_model,
            'wheel_radius': wheel_radius,
            'wheel_separation': wheel_separation,
            'control_rate_hz': 200.0,
            'kp': 1.8,
            'ki': 0.1,
            'kd': 0.05,
            'filter_alpha': 0.98
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot_model', default_value='ssl_robot',
                              description='Robot model: ssl_robot, turtlebot3_burger, jetbot'),
        DeclareLaunchArgument('scenario', default_value='straight_line',
                              description='Scenario: straight_line, circular_arc, m_shape'),
        DeclareLaunchArgument('target_velocity', default_value='1.2',
                              description='Target velocity in m/s'),
        DeclareLaunchArgument('tracking_mode', default_value='idealized_ground_truth',
                              description='idealized_ground_truth or vision_camera'),

        overhead_tracking_node,
        trajectory_generator_node,
        ltv_mpc_planner_node,
        simulated_pico_node
    ])
