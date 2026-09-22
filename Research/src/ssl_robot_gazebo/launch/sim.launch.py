import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_robot_desc = get_package_share_directory('ssl_robot_description')
    pkg_robot_gazebo = get_package_share_directory('ssl_robot_gazebo')

    # Arguments
    world_name = LaunchConfiguration('world_name', default='benchmark_arena.world')
    gui = LaunchConfiguration('gui', default='true')
    use_rviz = LaunchConfiguration('rviz', default='false')
    spawn_x = LaunchConfiguration('spawn_x', default='0.0')
    spawn_y = LaunchConfiguration('spawn_y', default='-2.0')
    spawn_z = LaunchConfiguration('spawn_z', default='0.03')
    spawn_yaw = LaunchConfiguration('spawn_yaw', default='0.0')

    world_path = PythonExpression([
        "'", os.path.join(pkg_robot_gazebo, 'worlds'), "/' + '", world_name, "'"
    ])

    # Robot Description via Xacro wrapped as ParameterValue for ROS 2 Humble
    xacro_file = os.path.join(pkg_robot_desc, 'urdf', 'robot.urdf.xacro')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # 1. Gazebo Server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    # 2. Gazebo Client (GUI)
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(gui)
    )

    # 3. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # 4. Spawn Robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_ssl_robot',
        output='screen',
        arguments=[
            '-entity', 'ssl_differential_robot',
            '-topic', 'robot_description',
            '-x', spawn_x,
            '-y', spawn_y,
            '-z', spawn_z,
            '-Y', spawn_yaw
        ]
    )

    # 5. RViz (Optional)
    rviz_config = os.path.join(pkg_robot_desc, 'rviz', 'ssl_robot.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world_name',
            default_value='benchmark_arena.world',
            description='World file name within ssl_robot_gazebo/worlds/'
        ),
        DeclareLaunchArgument('gui', default_value='true', description='Launch Gazebo GUI'),
        DeclareLaunchArgument('rviz', default_value='false', description='Launch RViz2'),
        DeclareLaunchArgument('spawn_x', default_value='0.0', description='Initial X coordinate'),
        DeclareLaunchArgument('spawn_y', default_value='-2.0', description='Initial Y coordinate'),
        DeclareLaunchArgument('spawn_z', default_value='0.03', description='Initial Z coordinate'),
        DeclareLaunchArgument('spawn_yaw', default_value='0.0', description='Initial Yaw angle'),

        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_robot,
        rviz
    ])
