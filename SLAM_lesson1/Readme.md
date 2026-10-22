# Robotics SLAM Hands-On Practical

This repo contains materials for conducting a practical lesson on ROS2-based SLAM stack.
The included launch files and configs support:
- Running SLAM using LIOSAM as the SLAM algorithm (Tightly coupled SLAM)
- Running SLAM using RtabMap as the SLAM algorithm (Loosely coupled SLAM)

This setup represents an example that roboticists would set up on a real-life robot application, as part of the SLAM pipeline. Bag files from previous trials and open-source datasets have been collected previously and will be used in this lesson. For those interested, you are highly encouraged to check out the papers that these codes are based on, namely [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](https://arxiv.org/abs/2007.00258) and [Rtabmap: Real-Time Appearance-Based Mapping](https://introlab.github.io/rtabmap/).

The lesson will proceed first using these bag files, to illustrate examples on how to visualize and setup these SLAM pipelines. After which, students are encouraged to deploy this on their respective robots and see the performance in real-life.

## Prerequisites
To improve reproducibility on different machines, the tutorial would be run using docker containers.
Install Docker on Ubuntu: [Docker Engine install guide](https://docs.docker.com/engine/install/ubuntu/).

For RViz GUIs and other custom GUIs from inside the container, allow Docker to use your display (run once per host session, on the host):

```bash
xhost +local:docker
```

For the visualization tools, Foxglove UI is recommended. Foxglove is a more modern-looking GUI compared to the traditional RViz2, able to support various functionalities typically needed in robotics applications, such as visualization of TF trees, 3D visualization, and native rendering of graphs and plots.

Visit [Foxglove Studio](https://foxglove.dev/) for more information and to download the application. The lesson would be conducted using Foxglove as the visualization tool primarily, but students are free to use whichever visualization tool they wish, although support for other tools may be limited.

For this lesson, some of the SLAM packages also has their own visualization tool included. Those would require display access when using it with containers as well.

## Setup

Run these commands from the `SLAM_lesson1` directory (where this `Readme`, `build.sh`, `Dockerfile`, and `compose.yml` live).

Build the image (first time, or after Dockerfile changes):
```bash
./build.sh
```
**Note:** Ideally this is done before class and a pre-built image is provided. If not, run `./build.sh` locally (it tags the image as `klass_slam_lesson1`).

Start the Zenoh router and lesson container in the background. Zenoh is the middleware that coordinates data between components.
```bash
docker compose up -d
```

Open a shell in the main lesson container:

```bash
docker exec -it klass_slam_lesson1 bash
```

The container sources ROS 2, the library workspace (LIO-SAM), and the lesson workspace automatically. Unless noted otherwise, **run all commands below inside this container**, each in its own terminal (`docker exec -it klass_slam_lesson1 bash`).

To stop the stack, run this on the host from `SLAM_lesson1`:

```bash
docker compose down
```

If you change files under `colcon_ws/src` (mounted at `/workspace/lesson/src`), rebuild inside the container:

```bash
cd /workspace/lesson/colcon_ws
# --parallel-workers is set to 2 so the build is less likely to overwhelm weaker machines.
# Increase or decrease as needed.
colcon build --packages-select mapping_lesson robot_description --parallel-workers 2
source install/setup.bash
```

## Mapping using LIO-SAM

Start the selected mapping launch in one container shell first. Then open a
second container shell for bag playback.

Starting the mapper before the bag prevents it from missing the first LiDAR and
IMU messages. Remember to only use one bag at a time.

### Newer College dataset

Run the mapper:

```bash
ros2 launch mapping_lesson newer_college.launch.py use_sim_time:=True
```

This loads the configuration specific to the dataset and runs the mapper.

In another terminal, play the bag. This command selects only the Ouster
point-cloud and IMU topics, applies the QoS overrides required by this converted
bag, publishes the bag clock, and starts playback paused:

```bash
ros2 bag play /workspace/lesson/bag_files/2021-07-01-10-37-38-quad-easy \
  --clock \
  --start-paused \
  --qos-profile-overrides-path /workspace/lesson/src/mapping_lesson/config/newer_college_bag_qos.yaml \
  --topics /os_cloud_node/points /os_cloud_node/imu
```

Press `Space` when the mapper is ready to start playback. Stop playback with
`Ctrl+C`.

### KLASS Ghost MacPherson dataset

Run the mapper:

```bash
ros2 launch mapping_lesson macpherson_ghost.launch.py use_sim_time:=True
```

In another terminal, play the bag using the command:

```bash
ros2 bag play /workspace/lesson/bag_files/ghost_macpherson_ros_imu \
  --clock \
  --start-paused
```

Press `Space` when the mapper is ready to start playback. Stop playback with
`Ctrl+C`.

### Saving maps

After bag playback finishes, leave the LIO-SAM launch running and call its save
service from another container shell. For example, to request 20 cm downsampling voxel, corner and
surface feature maps from the Ghost run with:

```bash
ros2 service call /lio_sam/save_map lio_sam/srv/SaveMap \
  "{resolution: 0.2, destination: '/workspace/lesson/maps/lio_sam_ghost'}"
```

For a Newer College run, use a different destination so the maps remain
separate:

```bash
ros2 service call /lio_sam/save_map lio_sam/srv/SaveMap \
  "{resolution: 0.2, destination: '/workspace/lesson/maps/lio_sam_newer_college'}"
```

Wait for `success: true` before stopping the LIO-SAM launch. Each destination
contains `GlobalMap.pcd`, `CornerMap.pcd`, `SurfMap.pcd`, `trajectory.pcd`, and
`transformations.pcd` and is visible in the host repo under `maps/`. The
requested resolution is applied to `CornerMap.pcd` and `SurfMap.pcd`;
`GlobalMap.pcd` contains their full-resolution combined cloud.

> **Important:** the LIO-SAM save service removes and recreates the entire
> destination directory. Always use a dedicated map directory, not
> `/workspace/lesson/maps` itself.

## Mapping using RTAB-Map

Start the selected mapping launch in one container shell first. Then open a
second container shell for bag playback.

Starting the mapper before the bag prevents it from missing the first LiDAR and
IMU messages. Remember to only use one bag at a time.

### Newer College dataset

Run the mapper:

```bash
ros2 launch mapping_lesson newer_college_rtabmap.launch.py use_sim_time:=True
```

In another terminal, play the bag. This command selects only the Ouster
point-cloud and IMU topics, applies the QoS overrides required by this converted
bag, publishes the bag clock, and starts playback paused:

```bash
ros2 bag play /workspace/lesson/bag_files/2021-07-01-10-37-38-quad-easy \
  --clock \
  --start-paused \
  --qos-profile-overrides-path /workspace/lesson/src/mapping_lesson/config/newer_college_bag_qos.yaml \
  --topics /os_cloud_node/points /os_cloud_node/imu
```

Press `Space` when the mapper is ready to start playback. Stop playback with
`Ctrl+C`.

### KLASS Ghost MacPherson dataset

Run the mapper:

```bash
ros2 launch mapping_lesson macpherson_ghost_rtabmap.launch.py use_sim_time:=True
```

In another terminal, play the bag using the command:

```bash
ros2 bag play /workspace/lesson/bag_files/ghost_macpherson_ros_imu \
  --clock \
  --start-paused
```

Press `Space` when the mapper is ready to start playback. Stop playback with
`Ctrl+C`.

The mapping database is written to `/workspace/lesson/maps/rtabmap.db` within
the container, which maps to `./maps/rtabmap.db`. Each RTAB-Map launch starts
with a fresh database, so rename or copy `rtabmap.db` after each run if you want
to keep maps from multiple datasets.

### Saving maps

RTAB-Map saves its working database continuously. After bag playback has
finished, stop the RTAB-Map launch cleanly with `Ctrl+C` so the database is
closed. Export the optimized LiDAR map, then convert the resulting PLY to a
broadly compatible ASCII PCD:

```bash
# Export the optimized LiDAR map from RTAB-Map
rtabmap-export \
  --cloud \
  --scan \
  --opt 2 \
  --voxel 0.05 \
  --output rtabmap \
  --output_dir /workspace/lesson/maps \
  /workspace/lesson/maps/rtabmap.db

# Convert the resulting PLY to a broadly compatible ASCII PCD
pcl_ply2pcd \
  -format 0 \
  /workspace/lesson/maps/rtabmap_cloud.ply \
  /workspace/lesson/maps/rtabmap_cloud.pcd
```

The PLY and ASCII PCD are written into the host repo's `maps/` directory.
Rename the database or use dataset-specific output filenames if you want to
preserve maps from multiple runs.

## Advanced Rtabmap

To start RTAB-Map's native visualization GUI, add
`use_rtabmap_viz:=true` to the selected mapping command. For example:

```bash
ros2 launch mapping_lesson newer_college_rtabmap.launch.py use_sim_time:=True use_rtabmap_viz:=true
```

Use `macpherson_ghost_rtabmap.launch.py` instead for the Ghost dataset.

## Closing remarks
Before a robot can navigate within a new environment, it first needs to estimate where it is—i.e., its pose in the environment. In modern robotics, this is typically accomplished via SLAM (Simultaneous Localization and Mapping), where the robot estimates both its pose and maps the environment at the same time. This is not an easy task for robots, because there are dependencies between the robot's estimation of its current pose and the map it creates. If there are errors in the pose estimate, then the map will also contain errors. This is commonly known as map drift. Without a robust algorithm to correct for drift, the robot will eventually be unable to localize itself.

For those new to the field, it would be good to understand the technical jargon typically used in SLAM literature. There are many variations of modern SLAM, but most can be broadly split into two components: a frontend and a backend. Think of the SLAM frontend as a module that estimates odometry—i.e., how much the robot has moved since the last update. With just the frontend, you might be able to get a pretty good estimate between consecutive time steps or even over a short period of time. However, after the robot travels for a long distance, the errors in the estimation add up, and the map drifts. That's where the backend comes in. The backend uses optimization to constrain the solution and bound the error. When a robot revisits a particular location, it can perform loop closure, adding more constraints to the solution to further improve and bound the error.

This practical is like a sneak peek into what you can do in SLAM, but it's not all-encompassing. Although most modern SLAM frameworks have switched from the older filter-based approach to factor-graph-based methods, especially for the backend, there are still many variations out there.
In this repo, we have two different ways of approaching the SLAM problem. RtabMap is a loosely coupled framework, and LIOSAM is a tightly coupled one. Long story short, a loosely coupled framework doesn't make any assumptions about your sensor configuration or robot modality, unlike tightly coupled frameworks. For instance, RtabMap is loosely coupled; it doesn't try to estimate hidden parameters relating to your sensors or robot modality. The framework itself simply requires an odometry source and a LiDAR point cloud for LiDAR odometry applications, and the SLAM pipeline just works.

Contrast this with LIOSAM, which explicitly estimates certain key characteristics of your IMU and then proactively uses the LiDAR estimate to correct errors in that estimate. See how there's a negative feedback loop? Consider a case where the IMU parameters are wrong, but LiDAR scan matching is able to compute the correct odometry because the environment has sufficient features. The correct estimate could then be used to reduce the error in your IMU parameter estimation, which would make your motion prediction more accurate at the next time step. That's the fundamental concept behind tightly coupled systems.

Feel free to explore different kinds of SLAM frameworks tailored to different robot configurations. For example, legged robots could use leg odometry and contact points to further improve the estimate—an approach commonly referred to as LIKO (LiDAR-Inertial-Kinematic Odometry). Or you could use a different type of filter. LIOSAM uses a factor-graph smoothing and optimization framework, but you could use things like extended Kalman filter variants. In particular, in recent literature, iterated error-state invariant formulations of EKFs have been quite popular.
