from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        Node(
            package='g13_prii3_turtlesim',
            executable='draw_number',
            name='draw_number'
        ),
    ])
