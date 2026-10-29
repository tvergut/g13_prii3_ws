from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    empty_world = PathJoinSubstitution([
        FindPackageShare('turtlebot3_gazebo'), 'launch', 'empty_world.launch.py'])

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle'),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(empty_world)),
        Node(
            package='g13_prii3_move_turtlebot',
            executable='collision_avoidance_sim',
            name='collision_avoidance_sim',
            parameters=[{'use_sim_time': True}]
        ),
    ])
