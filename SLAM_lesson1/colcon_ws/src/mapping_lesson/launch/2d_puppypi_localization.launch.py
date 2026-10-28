import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    LogInfo,
    RegisterEventHandler,
)
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    mapping_share = get_package_share_directory('mapping_lesson')

    posegraph = LaunchConfiguration('posegraph')
    slam_params_file = LaunchConfiguration('slam_params_file')
    odom_params_file = LaunchConfiguration('odom_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    localization_node = LifecycleNode(
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        output='screen',
        parameters=[
            slam_params_file,
            {
                'map_file_name': posegraph,
                'use_sim_time': use_sim_time,
            },
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'posegraph',
            default_value='/workspace/lesson/maps/puppypi',
            description=(
                'Serialized SLAM Toolbox pose-graph base path, without the '
                '.posegraph or .data extension.')),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(
                mapping_share, 'config', '2d_puppypi_localization.yaml'),
            description='SLAM Toolbox localization parameters file.'),
        DeclareLaunchArgument(
            'odom_params_file',
            default_value=os.path.join(
                mapping_share, 'config', '2d_puppypi_rtabmap.yaml'),
            description='RTAB-Map ICP odometry parameters file.'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock from a rosbag or simulator.'),

        Node(
            package='rtabmap_odom',
            executable='icp_odometry',
            namespace='rtabmap',
            name='icp_odometry',
            output='screen',
            parameters=[
                odom_params_file,
                {'use_sim_time': use_sim_time},
            ],
            remappings=[
                ('scan', '/scan'),
                ('odom', '/rtabmap/odom'),
            ],
        ),
        localization_node,
        EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(localization_node),
            transition_id=Transition.TRANSITION_CONFIGURE,
        )),
        RegisterEventHandler(
            OnStateTransition(
                target_lifecycle_node=localization_node,
                start_state='configuring',
                goal_state='inactive',
                entities=[
                    LogInfo(msg='SLAM Toolbox localization is activating.'),
                    EmitEvent(event=ChangeState(
                        lifecycle_node_matcher=matches_action(localization_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )),
                ],
            ),
        ),
    ])
