import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_robot_gazebo = get_package_share_directory('ssl_robot_gazebo')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_robot_gazebo, 'launch', 'sim.launch.py')
        ),
        launch_arguments={
            'world_name': 'ssl_field.world',
            'spawn_x': '0.0',
            'spawn_y': '0.0',
            'spawn_z': '0.03',
            'spawn_yaw': '0.0',
            'gui': 'true'
        }.items()
    )

    return LaunchDescription([sim_launch])
