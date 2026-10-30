import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('ssl_robot_gazebo')
    pkg_control = get_package_share_directory('ssl_robot_control')

    robot_model = LaunchConfiguration('robot_model', default='ssl_robot')
    scenario = LaunchConfiguration('scenario', default='straight_line')
    gui = LaunchConfiguration('gui', default='false')
    total_trials = LaunchConfiguration('total_trials', default='1')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'sim.launch.py')
        ),
        launch_arguments={'gui': gui, 'world_name': 'benchmark_arena.world', 'robot_model': robot_model, 'scenario': scenario, 'start_control': 'false'}.items()
    )

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_control, 'launch', 'control.launch.py')
        ),
        launch_arguments={'scenario': scenario, 'robot_model': robot_model}.items()
    )

    orchestrator_node = Node(
        package='ssl_robot_benchmarking',
        executable='trial_orchestrator',
        name='trial_orchestrator',
        output='screen',
        parameters=[{
            'robot_model': robot_model,
            'total_trials': total_trials,
            'output_dir': '/ros2_ws/benchmark_results'
        }]
    )

    trajectory_evaluator_node = Node(
        package='ssl_robot_benchmarking',
        executable='trajectory_evaluator',
        name='trajectory_evaluator',
        output='screen',
        parameters=[{
            'scenario_name': scenario
        }]
    )

    shutdown_on_orchestrator_exit = RegisterEventHandler(
        OnProcessExit(
            target_action=orchestrator_node,
            on_exit=[
                EmitEvent(event=Shutdown(reason='Benchmarking trials completed successfully.'))
            ]
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot_model', default_value='ssl_robot',
                              description='Robot model: ssl_robot, turtlebot3_burger, jetbot'),
        DeclareLaunchArgument('scenario', default_value='straight_line',
                              description='Scenario to benchmark: straight_line, circular_arc, m_shape'),
        DeclareLaunchArgument('gui', default_value='false',
                              description='Set to true to launch Gazebo GUI'),
        DeclareLaunchArgument('total_trials', default_value='1',
                              description='Number of trials for the orchestrator'),

        sim_launch,
        control_launch,
        orchestrator_node,
        trajectory_evaluator_node,
        shutdown_on_orchestrator_exit
    ])

