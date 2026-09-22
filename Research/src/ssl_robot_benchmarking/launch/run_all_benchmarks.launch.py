import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('ssl_robot_gazebo')
    pkg_control = get_package_share_directory('ssl_robot_control')

    scenario = LaunchConfiguration('scenario', default='straight_line')
    gui = LaunchConfiguration('gui', default='false')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'sim.launch.py')
        ),
        launch_arguments={'gui': gui, 'world_name': 'benchmark_arena.world'}.items()
    )

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_control, 'launch', 'control.launch.py')
        ),
        launch_arguments={'scenario': scenario}.items()
    )

    orchestrator_node = Node(
        package='ssl_robot_benchmarking',
        executable='trial_orchestrator',
        name='trial_orchestrator',
        output='screen',
        parameters=[{
            'total_trials': 10,
            'output_dir': '/ros2_ws/benchmark_results'
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('scenario', default_value='straight_line',
                              description='Scenario to benchmark: straight_line, circular_arc, m_shape'),
        DeclareLaunchArgument('gui', default_value='false',
                              description='Set to true to launch Gazebo GUI'),

        sim_launch,
        control_launch,
        orchestrator_node
    ])
