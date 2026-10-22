import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    mapping_share = get_package_share_directory('mapping_lesson')
    robot_share = get_package_share_directory('robot_description')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    xacro_path = os.path.join(robot_share, 'urdf', 'ghost.urdf.xacro')
    gui_config = os.path.join(
        mapping_share, 'config', 'rtabmapGUI.ini')

    rtabmap_remappings = [
        ('scan_cloud', '/velodyne_points'),
        ('imu', '/imu'),
        ('odom', '/rtabmap/odom'),
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(mapping_share, 'config', 'rtabmap.yaml'),
            description='RTAB-Map ROS parameters file.'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock from a rosbag or simulator.'),
        DeclareLaunchArgument(
            'use_rtabmap_viz',
            default_value='false',
            description='Start the native RTAB-Map visualization GUI.'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(
                    Command(['xacro', ' ', xacro_path]),
                    value_type=str),
                'use_sim_time': use_sim_time,
            }],
        ),
        Node(
            package='rtabmap_odom',
            executable='icp_odometry',
            namespace='rtabmap',
            name='icp_odometry',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=rtabmap_remappings,
        ),
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            namespace='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=rtabmap_remappings,
            arguments=['--delete_db_on_start'],
        ),
        # RTAB-Map Core starts at warning level. The ROS 2 service waits for
        # the SLAM node and enables info-level proximity/ICP diagnostics on
        # every launch.
        ExecuteProcess(
            cmd=[
                'ros2', 'service', 'call',
                '/rtabmap/rtabmap/log_info',
                'std_srvs/srv/Empty', '{}',
            ],
            output='screen',
        ),
        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            namespace='rtabmap',
            name='rtabmap_viz',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=rtabmap_remappings,
            arguments=['-d', gui_config],
            condition=IfCondition(LaunchConfiguration('use_rtabmap_viz')),
        ),
    ])
