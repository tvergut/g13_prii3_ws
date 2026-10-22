import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true'),
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle_pi'),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_dir, 'launch', 'empty_world.launch.py')),
            condition=IfCondition(LaunchConfiguration('sim'))
        ),
        Node(
            package='g13_prii3_move_turtlebot',
            executable='draw_number',
            name='draw_number',
            parameters=[{'use_sim_time': LaunchConfiguration('sim')}]
        ),
    ])
