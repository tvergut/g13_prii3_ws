import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle'),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_dir, 'launch', 'empty_world.launch.py'))
        ),
        Node(
            package='g13_prii3_move_turtlebot',
            executable='obstacle_stop',
            name='obstacle_stop',
            parameters=[{'use_sim_time': True}]
        ),
    ])
