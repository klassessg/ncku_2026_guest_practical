import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    mapping_share = get_package_share_directory('mapping_lesson')
    slam_toolbox_share = get_package_share_directory('slam_toolbox')

    params_file = LaunchConfiguration('params_file')
    slam_params_file = LaunchConfiguration('slam_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    rtabmap_remappings = [
        ('scan', '/scan'),
        ('odom', '/rtabmap/odom'),
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(
                mapping_share, 'config', '2d_puppypi_rtabmap.yaml'),
            description='RTAB-Map ROS parameters file.'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock from the puppypi_test rosbag.'),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(
                mapping_share,
                'config',
                '2d_puppypi_slam_toolbox.yaml'),
            description='SLAM Toolbox parameters file.'),

        Node(
            package='rtabmap_odom',
            executable='icp_odometry',
            namespace='rtabmap',
            name='icp_odometry',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=rtabmap_remappings,
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                slam_toolbox_share, 'launch', 'online_async_launch.py')),
            launch_arguments={
                'slam_params_file': slam_params_file,
                'use_sim_time': use_sim_time,
            }.items(),
        ),
    ])
