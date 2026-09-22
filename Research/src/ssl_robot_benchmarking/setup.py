import os
from glob import glob
from setuptools import setup

package_name = 'ssl_robot_benchmarking'

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
    description='Automated benchmarking and statistical verification for SSL differential robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sprint_halt_evaluator = ssl_robot_benchmarking.sprint_halt_evaluator:main',
            'trajectory_evaluator = ssl_robot_benchmarking.trajectory_evaluator:main',
            'latency_evaluator = ssl_robot_benchmarking.latency_evaluator:main',
            'trial_orchestrator = ssl_robot_benchmarking.trial_orchestrator:main',
        ],
    },
)
