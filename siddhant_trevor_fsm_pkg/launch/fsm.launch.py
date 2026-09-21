from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = 'siddhant_trevor_fsm_pkg'
    return LaunchDescription([
        Node(package=pkg, executable='detect_wall', output='screen'),
        Node(package=pkg, executable='wall_follow', output='screen'),
        Node(package=pkg, executable='draw_shape', output='screen'),
    ])
