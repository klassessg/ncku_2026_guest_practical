import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

"""
Convenience launcher wrapper to set the correct QoS overrides for the Newer College rosbag.
"""

def generate_launch_description():

    share_dir = get_package_share_directory('mapping_lesson')
    bag_qos_path = os.path.join(share_dir, 'config', 'newer_college_bag_qos.yaml')
    colcon_ws = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(share_dir))))
    default_bag = os.path.join(
        os.path.dirname(colcon_ws),
        'bag_files', '2021-07-01-10-37-38-quad-easy')

    bag_file_declare = DeclareLaunchArgument(
        'bag_file',
        default_value=default_bag,
        description='Path to the Newer College rosbag directory or .db3 file.')
    play_bag_declare = DeclareLaunchArgument(
        'play_bag',
        default_value='true',
        description='If true, play bag_file with QoS overrides for LIO-SAM.')

    return LaunchDescription([
        bag_file_declare,
        play_bag_declare,
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'play',
                LaunchConfiguration('bag_file'),
                '--clock',
                '--qos-profile-overrides-path', bag_qos_path,
                '--topics', '/os_cloud_node/points', '/os_cloud_node/imu',
            ],
            output='screen',
            condition=IfCondition(LaunchConfiguration('play_bag')),
        ),
    ])
