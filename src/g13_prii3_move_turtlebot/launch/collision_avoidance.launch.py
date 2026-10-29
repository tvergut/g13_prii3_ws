from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='g13_prii3_move_turtlebot',
            executable='collision_avoidance',
            name='collision_avoidance'
        ),
    ])
