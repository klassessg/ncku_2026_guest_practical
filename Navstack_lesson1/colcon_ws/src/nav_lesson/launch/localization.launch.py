import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory("nav_lesson")
    params_file = LaunchConfiguration("params_file")
    map_path = LaunchConfiguration("pcd_path")
    map_yaml = LaunchConfiguration("map")
    use_sim_time = LaunchConfiguration("use_sim_time")

    default_params = os.path.join(pkg_dir, "config", "localization.yaml")
    default_map_pcd = os.path.join(pkg_dir, "maps", "small_house", "map.pcd")
    default_map_yaml = os.path.join(pkg_dir, "maps", "small_house", "map.yaml")

    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time, "yaml_filename": map_yaml},
        ],
    )

    lidar_localization = Node(
        package="lidar_localization_ros2",
        executable="lidar_localization_node",
        name="lidar_localization",
        output="screen",
        parameters=[
            params_file,
            {
                "use_sim_time": use_sim_time,
                "map_path": map_path,
            },
        ],
        remappings=[
            ("/cloud", "/points"),
            ("/map", "/input_pointcloud_map"),
            ("/initial_map", "/pointcloud_map"),
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["map_server", "lidar_localization"],
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=default_params,
                description="Path to lidar_localization_ros2 parameters.",
            ),
            DeclareLaunchArgument(
                "pcd_path",
                default_value=default_map_pcd,
                description="Path to the PCD map for localization.",
            ),
            DeclareLaunchArgument(
                "map",
                default_value=default_map_yaml,
                description="Full path to Nav2 map yaml (map.pgm + map.yaml from pcd_to_nav2_map).",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation (Gazebo) clock if true",
            ),
            map_server,
            lidar_localization,
            lifecycle_manager,
        ]
    )
