import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import LoadComposableNodes, Node, SetParameter
from launch_ros.descriptions import ComposableNode, ParameterFile
from nav2_common.launch import RewrittenYaml

NAV_LIFECYCLE_NODES = [
    "controller_server",
    "smoother_server",
    "planner_server",
    "behavior_server",
    "velocity_smoother",
    "bt_navigator",
]

TF_REMAPPINGS = [("/tf", "tf"), ("/tf_static", "tf_static")]
CMD_VEL_REMAP = [("cmd_vel", "cmd_vel_nav"), ("cmd_vel_smoothed", "cmd_vel")]
CONTAINER_NAME = "nav_container"
AUTOSTART = True


def generate_launch_description():
    pkg_dir = get_package_share_directory("nav_lesson")

    use_sim_time = LaunchConfiguration("use_sim_time")
    params_file = LaunchConfiguration("params_file")
    use_composable = LaunchConfiguration("use_composable")

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key="",
            param_rewrites={},
            convert_types=True,
        ),
        allow_substs=True,
    )

    lifecycle_manager_params = {
        "use_sim_time": use_sim_time,
        "autostart": AUTOSTART,
        "node_names": NAV_LIFECYCLE_NODES,
    }

    standalone_nodes = GroupAction(
        condition=IfCondition(
            PythonExpression(["'", use_composable, "' != 'true'"])
        ),
        actions=[
            SetParameter("use_sim_time", use_sim_time),
            Node(
                package="nav2_controller",
                executable="controller_server",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
            ),
            Node(
                package="nav2_smoother",
                executable="smoother_server",
                name="smoother_server",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS,
            ),
            Node(
                package="nav2_planner",
                executable="planner_server",
                name="planner_server",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS,
            ),
            Node(
                package="nav2_behaviors",
                executable="behavior_server",
                name="behavior_server",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
            ),
            Node(
                package="nav2_velocity_smoother",
                executable="velocity_smoother",
                name="velocity_smoother",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
            ),
            Node(
                package="nav2_bt_navigator",
                executable="bt_navigator",
                name="bt_navigator",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS,
            ),
            Node(
                package="nav2_lifecycle_manager",
                executable="lifecycle_manager",
                name="lifecycle_manager_navigation",
                output="screen",
                parameters=[lifecycle_manager_params],
            ),
        ],
    )

    composable_nodes = GroupAction(
        condition=IfCondition(
            PythonExpression(["'", use_composable, "' == 'true'"])
        ),
        actions=[
            SetParameter("use_sim_time", use_sim_time),
            Node(
                name=CONTAINER_NAME,
                package="rclcpp_components",
                executable="component_container_isolated",
                output="screen",
                parameters=[configured_params],
                remappings=TF_REMAPPINGS,
            ),
            LoadComposableNodes(
                target_container=CONTAINER_NAME,
                composable_node_descriptions=[
                    ComposableNode(
                        package="nav2_controller",
                        plugin="nav2_controller::ControllerServer",
                        name="controller_server",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
                    ),
                    ComposableNode(
                        package="nav2_smoother",
                        plugin="nav2_smoother::SmootherServer",
                        name="smoother_server",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS,
                    ),
                    ComposableNode(
                        package="nav2_planner",
                        plugin="nav2_planner::PlannerServer",
                        name="planner_server",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS,
                    ),
                    ComposableNode(
                        package="nav2_behaviors",
                        plugin="behavior_server::BehaviorServer",
                        name="behavior_server",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
                    ),
                    ComposableNode(
                        package="nav2_velocity_smoother",
                        plugin="nav2_velocity_smoother::VelocitySmoother",
                        name="velocity_smoother",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS + CMD_VEL_REMAP,
                    ),
                    ComposableNode(
                        package="nav2_bt_navigator",
                        plugin="nav2_bt_navigator::BtNavigator",
                        name="bt_navigator",
                        parameters=[configured_params],
                        remappings=TF_REMAPPINGS,
                    ),
                    ComposableNode(
                        package="nav2_lifecycle_manager",
                        plugin="nav2_lifecycle_manager::LifecycleManager",
                        name="lifecycle_manager_navigation",
                        parameters=[lifecycle_manager_params],
                    ),
                ],
            ),
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation clock",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(
                    pkg_dir, "config", "navigation.yaml"
                ),
                description="Nav2 params for turtlebot3_burger",
            ),
            DeclareLaunchArgument(
                "use_composable",
                default_value="true",
                description="Run Nav2 nodes in a component container",
            ),
            standalone_nodes,
            composable_nodes,
        ]
    )
