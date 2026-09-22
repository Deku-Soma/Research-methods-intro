import os
from glob import glob
from setuptools import setup

package_name = 'ssl_robot_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='SashinS',
    maintainer_email='researcher@university.ac.za',
    description='Dual-loop control architecture and overhead tracking for SSL differential robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'overhead_tracking_node = ssl_robot_control.overhead_tracking_node:main',
            'trajectory_generator = ssl_robot_control.trajectory_generator:main',
            'ltv_mpc_planner = ssl_robot_control.ltv_mpc_planner:main',
            'simulated_pico_firmware = ssl_robot_control.simulated_pico_firmware:main',
        ],
    },
)
