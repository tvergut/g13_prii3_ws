from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    empty_world = PathJoinSubstitution([
        FindPackageShare('turtlebot3_gazebo'), 'launch', 'empty_world.launch.py'])

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='true'),
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle_pi'),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(empty_world),
            condition=IfCondition(LaunchConfiguration('sim'))
        ),
        Node(
            package='g13_prii3_move_turtlebot',
            executable='draw_number',
            name='draw_number',
            parameters=[{'use_sim_time': LaunchConfiguration('sim')}]
        ),
    ])
