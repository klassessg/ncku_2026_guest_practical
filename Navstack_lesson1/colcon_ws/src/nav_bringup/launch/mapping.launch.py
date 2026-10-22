import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition


def generate_launch_description():
    pkg_dir = get_package_share_directory("nav_bringup")
    parameter_file = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    launch_rviz = LaunchConfiguration("launch_rviz")

    default_params = os.path.join(pkg_dir, "config", "mapping.yaml")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="Path to the LIO-SAM parameters file.",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation (Gazebo) clock if true",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                description="Launch RViz2 if true",
            ),
            # Initial map->odom (LIO-SAM updates mapping odometry; same pattern as SLAM lesson)
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                arguments=[
                    "--x",
                    "0.0",
                    "--y",
                    "0.0",
                    "--z",
                    "0.0",
                    "--roll",
                    "0.0",
                    "--pitch",
                    "0.0",
                    "--yaw",
                    "0.0",
                    "--frame-id",
                    "map",
                    "--child-frame-id",
                    "odom",
                ],
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            Node(
                package="lio_sam",
                executable="lio_sam_imuPreintegration",
                parameters=[parameter_file, {"use_sim_time": use_sim_time}],
                output="screen",
            ),
            Node(
                package="lio_sam",
                executable="lio_sam_imageProjection",
                name="lio_sam_imageProjection",
                parameters=[parameter_file, {"use_sim_time": use_sim_time}],
                output="screen",
            ),
            Node(
                package="lio_sam",
                executable="lio_sam_featureExtraction",
                name="lio_sam_featureExtraction",
                parameters=[parameter_file, {"use_sim_time": use_sim_time}],
                output="screen",
            ),
            Node(
                package="lio_sam",
                executable="lio_sam_mapOptimization",
                name="lio_sam_mapOptimization",
                parameters=[parameter_file, {"use_sim_time": use_sim_time}],
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", os.path.join(pkg_dir, "rviz", "mapping.rviz")],
                output="screen",
                condition=IfCondition(launch_rviz),
            ),
        ]
    )
