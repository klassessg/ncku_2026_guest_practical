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
    filtered_imu_topic = '/rtabmap/imu/filtered'
    xacro_path = os.path.join(
        robot_share, 'urdf', 'newer_college.urdf.xacro')
    gui_config = os.path.join(
        mapping_share, 'config', 'rtabmapGUI.ini')

    rtabmap_remappings = [
        ('scan_cloud', '/os_cloud_node/points'),
        ('imu', filtered_imu_topic),
        ('odom', '/rtabmap/odom'),
    ]
    best_effort_qos = {
        'qos': 2,
        'qos_imu': 2,
    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(mapping_share, 'config', 'rtabmap.yaml'),
            description='RTAB-Map ROS parameters file.'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use /clock from the Newer College rosbag.'),
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
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            namespace='rtabmap',
            name='imu_filter',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'use_mag': False,
                'publish_tf': False,
                'world_frame': 'enu',
            }],
            remappings=[
                ('imu/data_raw', '/os_cloud_node/imu'),
                ('imu/data', filtered_imu_topic),
            ],
        ),
        Node(
            package='rtabmap_odom',
            executable='icp_odometry',
            namespace='rtabmap',
            name='icp_odometry',
            output='screen',
            parameters=[
                params_file,
                {'use_sim_time': use_sim_time},
                best_effort_qos,
            ],
            remappings=rtabmap_remappings,
        ),
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            namespace='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=[
                params_file,
                {
                    'use_sim_time': use_sim_time,
                    'qos_scan': 2,
                    'qos_odom': 2,
                },
            ],
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
            parameters=[
                params_file,
                {
                    'use_sim_time': use_sim_time,
                    'qos_scan': 2,
                    'qos_odom': 2,
                },
            ],
            remappings=rtabmap_remappings,
            arguments=['-d', gui_config],
            condition=IfCondition(LaunchConfiguration('use_rtabmap_viz')),
        ),
    ])
