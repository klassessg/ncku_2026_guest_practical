import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = get_package_share_directory("nav_bringup")
    ros_gz_sim_dir = get_package_share_directory("ros_gz_sim")
    gazebo_resources_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "..",
            "..",
            "..",
            "lesson",
            "gazebo_resources",
        )
    )
    print(f"===> Gazebo resources directory: {gazebo_resources_dir}")

    use_sim_time = LaunchConfiguration("use_sim_time")
    gui = LaunchConfiguration("gui")
    world = LaunchConfiguration("world_path")

    default_world = os.path.join(
        gazebo_resources_dir,
        "worlds",
        "small_house",
        "small_house_simple.world",
    )
    bridge_params = os.path.join(pkg_dir, "config", "turtlebot3_burger_bridge.yaml")
    xacro_path = os.path.join(pkg_dir, "urdf", "turtlebot.urdf.xacro")
    
    # Add the models
    resource_paths = []
    for path in os.listdir(os.path.join(gazebo_resources_dir, "worlds")):
        resource_paths.append(os.path.join(gazebo_resources_dir, "worlds", path))
        model_dir = os.path.join(os.path.join(gazebo_resources_dir, "worlds"), path, "models")
        if os.path.exists(model_dir):
            print(f"Models exist for world '{path}': {model_dir}")
            resource_paths.append(model_dir)
        else:
            print(f"No models found for world '{path}' at {model_dir}")

    robots = os.path.join(gazebo_resources_dir, "robots")
    gz_resource_path = AppendEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=f"{':'.join(resource_paths)}:{robots}",
    )

    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_dir, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": ["-r -s -v2 ", world],
            "on_exit_shutdown": "true",
        }.items(),
    )

    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_dir, "launch", "gz_sim.launch.py")
        ),
        condition=IfCondition(gui),
        launch_arguments={
            "gz_args": "-g -v2 ",
            "on_exit_shutdown": "true",
        }.items(),
    )

    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[
            {
                "config_file": bridge_params,
                "use_sim_time": use_sim_time,
            }
        ],
        output="screen",
    )
    
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "robot_description": ParameterValue(
                    Command(["xacro", " ", xacro_path]),
                    value_type=str,
                ),
            }
        ],
        output="screen",
    )
    
    static_transform_publisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation clock on bridge and downstream nodes",
            ),
            DeclareLaunchArgument(
                "gui",
                default_value="true",
                description="Start Gazebo GUI (gz client)",
            ),
            DeclareLaunchArgument(
                "world_path",
                default_value=default_world,
                description="Full path to the Gazebo Sim world SDF",
            ),
            gz_resource_path,
            gz_server,
            gz_client,
            ros_gz_bridge,
            robot_state_publisher,
            static_transform_publisher,
        ]
    )
