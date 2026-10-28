# Mapping with PuppyPi and SLAM Toolbox

The PuppyPi 2D mapping launch combines two ROS 2 nodes:

- RTAB-Map's `icp_odometry` estimates `odom -> base_footprint` from `/scan`.
- SLAM Toolbox consumes the scan, odometry, and robot TF, builds the occupancy
  grid on `/map`, and publishes `map -> odom`.

The launch is intended for bag files gathered from live
PuppyPi or running on PuppyPi.

## Before starting

Follow the container setup in the lesson's [main README](../../../Readme.md).
Run the commands below inside `klass_slam_lesson1`; open a new container shell
for each terminal shown.

If `mapping_lesson` has not been built since the PuppyPi launch or configuration
was added, build and source it:

```bash
cd /workspace/lesson/colcon_ws
colcon build --packages-select mapping_lesson --parallel-workers 2
source install/setup.bash
```

The pipeline requires these inputs:

- `/scan` (`sensor_msgs/msg/LaserScan`)
- a TF transform between `base_footprint` and the laser frame named in each
  scan's `header.frame_id`

## Map using Puppypi bag

Start the mapper before starting playback so it does not miss the first scan or
TF messages:

```bash
ros2 launch mapping_lesson 2d_puppypi_mapping.launch.py use_sim_time:=True
```

In a second container shell, start the bag paused and publish its clock:

```bash
ros2 bag play /workspace/lesson/bag_files/puppypi_test \
  --clock \
  --start-paused \
  --topics /scan /tf
```

Press `Space` once the mapping nodes are ready.

## Map with a live PuppyPi

Connect PuppyPi with ros1-to-ros2 bridge.

Confirm that the computer can see the required data:

```bash
ros2 topic hz /scan
ros2 topic echo /scan --once --field header.frame_id
ros2 run tf2_ros tf2_echo base_footprint <laser_frame>
```

Replace `<laser_frame>` with the frame reported by the second command. Then
start mapping with wall time instead of bag time:

```bash
ros2 launch mapping_lesson 2d_puppypi_mapping.launch.py
```

Drive slowly while building the map. Avoid rapid turns, keep visible walls or
other geometry within LiDAR range, and revisit previously mapped areas to give
SLAM Toolbox opportunities for loop closure.

In this setup, SLAM Toolbox publishes `map -> odom`, ICP odometry publishes `odom -> base_footprint`, and the robot or
bag supplies `base_footprint -> laser frame`.

## Save the map

Leave the mapper running and save both forms of the map from another container
shell. Save the occupancy grid used for visualization and other map consumers:

```bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: '/workspace/lesson/maps/puppypi'}}"
```
This writes `puppypi.yaml` and `puppypi.pgm` to `SLAM_lesson1/maps/` on the
host. Use a new base name for each run if you want to retain multiple maps.

SLAM Toolbox localization uses the serialized pose graph, not the occupancy
grid. Save it with the same base name:

```bash
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/workspace/lesson/maps/puppypi'}"
```

This writes the paired `puppypi.posegraph` and `puppypi.data` files. Keep both
files together; both are required when loading the serialized map. Use a new
base name for each run if you want to retain multiple maps.

Wait for a successful response from both services before stopping the launch
with `Ctrl+C`.

## Localize on a saved map

The localization launch loads the serialized SLAM Toolbox pose graph saved
above. RTAB-Map ICP odometry publishes `odom -> base_footprint`, while SLAM
Toolbox matches `/scan` against the pose graph and publishes `map -> odom`.

For a live PuppyPi, start its LiDAR and TF publishers, then run:

```bash
ros2 launch mapping_lesson 2d_puppypi_localization.launch.py
```

The default pose-graph base path is `/workspace/lesson/maps/puppypi`. To use
another saved pose graph, pass its base path without the `.posegraph` or `.data`
extension:

```bash
ros2 launch mapping_lesson 2d_puppypi_localization.launch.py \
  posegraph:=/workspace/lesson/maps/another_map
```

Set the robot's initial pose in the `map` frame with Foxglove or RViz's
**2D Pose Estimate** tool if the robot did not start near the map origin. SLAM
Toolbox subscribes to `/initialpose` and uses subsequent scans to refine the
estimate.

## Troubleshooting steps

Common failure modes:

- **Nothing advances during bag playback:** the bag was not started with
  `--clock`, or the mapper was launched with `use_sim_time:=false`.
- **ICP reports a missing transform:** the scan's frame cannot be transformed
  to `base_footprint`. Check the scan frame and the robot/bag TF data.
- **`/scan` exists but `/rtabmap/odom` does not:** check scan ranges and timing,
  then review the ICP limits in `config/2d_puppypi_rtabmap.yaml`.
- **Localization cannot deserialize the map:** confirm the matching `.posegraph`
  and `.data` files are together and pass their base path without an extension.
- **The map smears or jumps:** move more slowly, ensure there are enough nearby
  geometric features, and verify that no second node publishes
  `odom -> base_footprint`.
- **The map updates too slowly or rejects motion:** tune
  `minimum_time_interval`, `minimum_travel_distance`, and
  `minimum_travel_heading` in `config/2d_puppypi_slam_toolbox.yaml`.
