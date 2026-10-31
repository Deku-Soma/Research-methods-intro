import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_robot_desc = get_package_share_directory('ssl_robot_description')
    pkg_robot_gazebo = get_package_share_directory('ssl_robot_gazebo')
    pkg_control = get_package_share_directory('ssl_robot_control')

    # Arguments
    world_name = LaunchConfiguration('world_name', default='benchmark_arena.world')
    gui = LaunchConfiguration('gui', default='true')
    use_rviz = LaunchConfiguration('rviz', default='false')
    scenario = LaunchConfiguration('scenario', default='straight_line')
    start_control = LaunchConfiguration('start_control', default='true')

    default_x = PythonExpression(["'1.0' if '", scenario, "' == 'circular_arc' else '0.0'"])
    default_y = PythonExpression(["'0.0' if '", scenario, "' == 'circular_arc' else ('1.0' if '", scenario, "' == 'm_shape' else '-2.0')"])
    default_yaw = PythonExpression(["'1.570796' if '", scenario, "' == 'circular_arc' else ('1.107149' if '", scenario, "' == 'm_shape' else '0.0')"])

    spawn_x = LaunchConfiguration('spawn_x', default=default_x)
    spawn_y = LaunchConfiguration('spawn_y', default=default_y)
    spawn_z = LaunchConfiguration('spawn_z', default='0.03')
    spawn_yaw = LaunchConfiguration('spawn_yaw', default=default_yaw)

    robot_model = LaunchConfiguration('robot_model', default='ssl_robot')

    world_path = PathJoinSubstitution([
        pkg_robot_gazebo, 'worlds', world_name
    ])

    # Dynamic Robot Description via Xacro selection based on robot_model
    xacro_filename = PythonExpression([
        "'turtlebot3_burger.urdf.xacro' if '", robot_model, "' == 'turtlebot3_burger' else (",
        "'jetbot.urdf.xacro' if '", robot_model, "' == 'jetbot' else 'robot.urdf.xacro')"
    ])
    xacro_file = PathJoinSubstitution([
        pkg_robot_desc, 'urdf', xacro_filename
    ])
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
            '-entity', robot_model,
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

    # 6. Controller stack (Optional, default true for interactive sim)
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_control, 'launch', 'control.launch.py')
        ),
        launch_arguments={'scenario': scenario, 'robot_model': robot_model}.items(),
        condition=IfCondition(start_control)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_model',
            default_value='ssl_robot',
            description='Model to simulate: ssl_robot, turtlebot3_burger, jetbot'
        ),
        DeclareLaunchArgument(
            'world_name',
            default_value='benchmark_arena.world',
            description='World file name within ssl_robot_gazebo/worlds/'
        ),
        DeclareLaunchArgument('gui', default_value='true', description='Launch Gazebo GUI'),
        DeclareLaunchArgument('rviz', default_value='false', description='Launch RViz2'),
        DeclareLaunchArgument('scenario', default_value='straight_line', description='Benchmark scenario'),
        DeclareLaunchArgument('start_control', default_value='true', description='Launch control stack with simulation'),
        DeclareLaunchArgument('spawn_x', default_value=default_x, description='Initial X coordinate'),
        DeclareLaunchArgument('spawn_y', default_value=default_y, description='Initial Y coordinate'),
        DeclareLaunchArgument('spawn_z', default_value='0.03', description='Initial Z coordinate'),
        DeclareLaunchArgument('spawn_yaw', default_value=default_yaw, description='Initial Yaw angle'),

        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_robot,
        rviz,
        control_launch,
        Node(
            package='ssl_robot_benchmarking',
            executable='trajectory_evaluator',
            name='trajectory_evaluator',
            output='screen',
            parameters=[{'scenario_name': scenario}],
            condition=IfCondition(start_control)
        )
    ])

