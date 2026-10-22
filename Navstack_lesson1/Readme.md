# Robotics Navstack Hands-On Practical

This repo contains materials for conducting a practical lesson on deploying a standard ROS2-based navigation stack.
The included launch files and configs support:

1. Building a 3D point cloud map of the environment with the open-source LIO-SAM SLAM pipeline
2. Localizing against that map with NDT/ICP-based lidar localization
3. Point-to-point navigation with Nav2

The setup is adapted from the [Navigation2](https://nav2.org/) tutorials, but uses a TurtleBot3 with a 3D Velodyne-style lidar in Gazebo—closer to many real robots than the default 2D laser examples. The Nav2 documentation remains the best reference for integrating your own hardware, so you are extremely encouraged to check it out, using the link provided.

The MPPI controller used in this repo is slightly different from the one on the Nav2 Jazzy branch. Additional modifications have been made to port useful visualization changes to the package, to facilitate the learning and understanding of the package.

## Prerequisites

To improve reproducibility on different machines, the tutorial would be run using docker containers.
Install Docker on Ubuntu: [Docker Engine install guide](https://docs.docker.com/engine/install/ubuntu/).

For Gazebo and RViz GUIs from inside the container, allow Docker to use your display (run once per host session, on the host):

```bash
xhost +local:docker
```

For the visualization tools, Foxglove UI is recommended. Foxglove is a more modern-looking GUI compared to the traditional RViz2, able to support various functionalities typically needed in robotics applications, such as visualization of TF trees, 3D visualization, and native rendering of graphs and plots.

Visit [Foxglove Studio](https://foxglove.dev/) for more information and to download the application. The lesson would be conducted using Foxglove as the visualization tool primarily, but students are free to use whichever visualization tool they wish, although support for other tools may be limited.

## Setup

Run these commands from the `Navstack_lesson1` directory (where this `Readme`, `Dockerfile` and `compose.yml` live).

Build the image (first time, or after Dockerfile changes):
```bash
./build.sh
```
**Note: Ideally, this should have already been done prior to the class and a docker image should be provided. In the event that that's not available, you can build it yourself.**

Start the Zenoh router and lesson container in the background. Zenoh is the middleware that coordinates the exchange of data between various components in the system.
```bash
docker compose up -d
```

Open a shell in the main lesson container:

```bash
docker exec -it klass_navstack_lesson1 bash
```
The container sources ROS 2, the library workspace (LIO-SAM, localization), and the lesson workspace automatically. Unless noted otherwise, **run all commands below inside this container**, each in its own terminal (`docker exec -it klass_navstack_lesson1 bash`).

To stop the stack:
```bash
docker compose down
```

If you change files under `colcon_ws/src`, rebuild the lesson package inside the container:
```bash
cd /workspace/lesson/colcon_ws
# --parallel-workers is set to 2, so that the build doesn't crash weaker machines. Increase/decrease this
# as needed for your machine
colcon build --packages-select nav_bringup --parallel-workers 2
source install/setup.bash
```

### Launch the simulation

The world is based on the open-source [Gazebo worlds dataset](https://github.com/mlherd/Dataset-of-Gazebo-Worlds-Models-and-Maps/tree/master/worlds) and runs on Gazebo Sim. The robot is a TurtleBot3 Burger with a 16-beam GPU lidar (Velodyne-style point cloud on `/points`). See [Gazebo Sim getting started](https://gazebosim.org/docs/latest/getstarted/) for general simulator usage.

**Terminal 1 — simulation, bridge, and robot state**

Headless (server only, no Gazebo GUI):

```bash
ros2 launch nav_bringup sim.launch.py gui:=false
```

With Gazebo GUI (default):

```bash
ros2 launch nav_bringup sim.launch.py
```

To open the Gazebo GUI later while the server from `sim.launch.py` is already running:

```bash
gz sim -g
```

Optional: use the full `small_house` world instead of the simplified default:

```bash
ros2 launch nav_bringup sim.launch.py world_path:=/workspace/lesson/gazebo_resources/worlds/small_house/small_house.world
```

### Launch localization

For this lesson, a prebuilt map has been created beforehand, so that users can focus on the localization and navigation portions of the robotic stack.

*For those interested in how the map was originally built, see [Mapping (LIO-SAM)](#mapping-lio-sam) below.*

While the simulation is still running:

**Terminal 2 — 3D lidar localization**

The following command launches the localization stack and map server. This helps with the estimation of the robot's current position.

```bash
ros2 launch nav_bringup localization.launch.py use_sim_time:=true
```

Set the robot pose once using either Foxglove or RViz2 (**2D Pose Estimate**, fixed frame `map`).

If you want to use a custom map, override the map file if needed:

```bash
ros2 launch nav_bringup localization.launch.py use_sim_time:=true pcd_path:=/path/to/your/map.pcd
```

### Launch navigation

**Terminal 3 — Nav2**

Run the navigation stack. 

```bash
ros2 launch nav_bringup navigation.launch.py use_sim_time:=true
```

Send navigation goals via RViz (Nav2 goal tool) or Foxglove publisher. The default 2D occupancy map to be loaded for this lesson is bundled under `nav_bringup/maps/small_house/`; adjust the `map` launch argument if you use a different YAML.


## Exercises

### Exercise 1: Point-to-point navigation with Foxglove

For your first exercise, you'll use Foxglove to get the robot moving in simulation. The goal is to send any navigation target within the known occupancy map and observe the robot autonomously planning and following a path to reach it.

**Steps:**

1. **Open Foxglove:**  
   Launch Foxglove Studio in your browser and connect it to your ROS 2 system (`ws://localhost:8765` if running locally with the default bridge).

2. **Add the Publish Tool:**  
   - Click the **"Publish"** tool (plus icon in the sidebar).
   - Select the `/goal_pose` topic. This is the topic that the navigation stack listens to. In this lesson, it has been configured to be `/goal_pose` with the message type `geometry_msgs/msg/PoseStamped`.
   - If you're unsure which topic to use, check the "Topics" panel in Foxglove.

3. **Send a Goal:**  
   - Set the `Frame` to `map`.
   - In the Foxglove 3D or 2D map view, right-click on a navigable area of the map and select **"Publish Pose"**.
   - Specify a reasonable x/y target within the mapped area.

4. **Observe the Robot:**  
   - Once the goal is published, the navigation stack will compute the shortest path to the goal and the robot will begin moving autonomously.
   - You can observe the planned path and the robot's motion in Foxglove. The robot is represented using an axis with the label `base_link`, and the visualization topics are `/plan` and `/optimal_trajectory`.

**What you should see**  
The robot will plan a collision-free path around the static obstacles, then steadily follow the path until it reaches the goal, where it will stop. Try experimenting with different goal locations. 

- What happens when the goal you try to give is outside of the map?
- What happens when you give the goal very close to the obstacle?
- What happens when you give the goal in the opposite direction to where the robot is facing?

### Exercise 2: MPPI controller visualization

For this exercise, you'll use Foxglove to visualize how MPPI control works.

**Steps:**

1. **Send a Navigation Goal:**  
   - In Foxglove, use the steps from Exercise 1 to send a goal to your desired location on the map.

2. **Visualize the MPPI Controller Trajectories:**  
   - In Foxglove, open the "Topics" panel and enable visualization for the `/optimal_trajectory` topic.
   - Several colored lines will appear around the robot in the map view. These lines represent the different control trajectories considered by the MPPI controller as it plans the robot's movement in real-time.
   
3. **Observe the trajectories**
   - What do these trajectories represent? Think back to how MPPI works to find the optimal control.
   - What do the colors represent? 
   - Is there a particular shape to these trajectories? How does this shape relate to the mechanisms behind MPPI?
   
4. **Obstacle avoidance**
   - Using the Gazebo simulator GUI, add an obstacle to the environment. Because this obstacle is added during runtime, it will not appear in the pointcloud map.
   - Observe the trajectories. How do they adapt when the new obstacle is present?
   - Next, open the `navigation.yaml` file in `colcon_ws/src/nav_bringup/config/navigation.yaml`. Locate the `global_costmap.obstacle_layer` section and set `enabled` to `False`. Then rebuild the package by running the following from the `colcon_ws` directory:
     ```bash
     colcon build --packages-select nav_bringup
     ```
     Or, for quicker updates when editing Python or config files, run:
     ```bash
     colcon build --packages-select nav_bringup --symlink-install
     ```
   - After making this change, examine how the path published on **`/plan`** changes when you send a new goal. Does the path still avoid the added obstacle? Observe how the robot behaves in relation to this obstacle now that the global planner is not considering it.

5. **Free exploration** 
   - Explore the environment, try different goals, and experiment with different configuration settings within `navigation.yaml`.

## Rationale of the exercise
Robotic navigation is a complex task that is often approached hierarchically to manage both the scale and the complexity of the environment. These exercises are designed to illustrate one way to decompose this problem, by using two planners at different scales, a global planner and a local planner.

- **Global Planning** involves finding a high-level, collision-free path from the robot’s current position to the goal location, typically by considering a map of the environment. This handles the large-scale strategy — for example, deciding which rooms or corridors to follow in order to reach a distant goal, or, in the case of exploration, deciding where to go next.

- **Local Planning** takes over once the global path is set. It handles the real-time details of moving the robot, including avoiding unexpected obstacles, fine-tuning the path, and reacting to dynamic changes. The local planner ensures safe and smooth execution of the global plan, even as the environment or robot’s pose estimates change. For legged robots, this could become even more complicated when traversability constraints need to be accounted for.

For example, in multi-robot exploration or adaptive coverage, planners may have additional objectives: the global planner can assign different exploration regions to each robot, while the local planner could try to maximize area coverage rather than simply following the shortest route. This hierarchical approach allows for modularity and robustness — ensuring robots are able to achieve overall goals while handling local details and contingencies effectively.

These exercises offer a teaser into how to go about doing a navigation stack, as well as introducing some of the off-the-shelf implementations already offered by the ROS2 Navigation stack. Setting a goal invokes the global planner, and observing real-time movement engages the local planner. Understanding this split is fundamental for developing advanced autonomous robotic behaviors in realistic, dynamic environments.
You could integrate these packages into your applications as needed, instead of developing them from scratch, and focus more on the problem domain.

Additional concepts not covered in these exercises include how to handle the dynamic switching of tasks. ROS2 navigation supports the use of behavior trees, which is what is being used in this exercise internally to coordinate the navigation task. It's an incredibly powerful tool that allows a wide variety of behaviours. For more information, you can check out the [Nav2 webpage](https://navigation.ros.org/).


## Mapping (LIO-SAM)

With simulation running in terminal 1, start mapping in a second terminal:

```bash
ros2 launch nav_bringup mapping.launch.py use_sim_time:=true
```
Drive the robot in simulation to explore the environment. Parameters are in `colcon_ws/src/nav_bringup/config/mapping.yaml`. When map saving is enabled in that file, LIO-SAM can write PCD maps under `/tmp/lio_sam_maps/`, or you can call the `lio_sam/save_map` service while `lio_sam_mapOptimization` is running.

Here's an example command that will save the output under `/tmp/lio_sam_maps`.
```bash
ros2 service call /lio_sam/save_map lio_sam/srv/SaveMap "{resolution: 0.0, destination: '/tmp/lio_sam_maps/'}"
```
For example, to use it, copy the `GlobalMap.pcd` into `colcon_ws/src/nav_bringup/maps/small_house/map.pcd` for the small house example.

After you save a 3D point cloud map, generate the 2D pair that Nav2 and `map_server` use: `map.pgm` plus `map.yaml`. Run the conversion from the `nav_bringup` package root.

```bash
cd /workspace/lesson/colcon_ws/src/nav_bringup
./scripts/pcd_to_nav2_map.py maps/small_house/map.pcd \
  --z-min 0.0 --z-max 1.0 --resolution 0.05 --mark-free \
  --nav2-map-dir maps/small_house
```

The script keeps points with height in `[z-min, z-max]` (meters, map frame), rasterizes them at `--resolution` (meters per pixel), and writes both files into `--nav2-map-dir`. The example uses a 0.0–1.0 m slice; tune the band so walls and obstacles appear in the grid. You would want to configure this roughly based on your robot's size plus some tolerance. Add `--mark-free` so open cells are marked traversable instead of unknown.

If you generate new maps, shift (move) them into `/workspace/lesson/colcon_ws/src/nav_bringup/maps`.
Then, rebuild `nav_bringup` and re-source the workspace if you want to use them.
```bash
colcon build --packages-select nav_bringup && source install/setup.bash
```
