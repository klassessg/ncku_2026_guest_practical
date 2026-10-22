# ROS 1 to ROS 2 bridge

## Build the image

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge build
```

## Run the bridge

Start the bridge:

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge up -d klass_ros1_bridge
```

If you need the zenoh router and the ROS1 master, you can also start them using

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge run -d --rm \
  --name klass_zenoh_router klass_ros1_bridge \
  ros2 run rmw_zenoh_cpp rmw_zenohd

docker compose -f compose.ros1_bridge.yml --profile bridge run -d --rm \
  --name klass_roscore klass_ros1_bridge roscore
```

## Test to see if it works

Run these commands from the project root. The test bag must be at
`SLAM_lesson1/bag_files/corridor.bag`.

Play `corridor.bag` through ROS 1:

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge run -d --rm \
  -v "$PWD/SLAM_lesson1/bag_files:/bag_files:ro" \
  --name klass_corridor_player klass_ros1_bridge \
  rosbag play /bag_files/corridor.bag
```

## Check that it works

List the ROS 2 topics:

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge run --rm \
  klass_ros1_bridge ros2 topic list
```

You should see standard topics from the bag, including `/imu_raw`,
`/points_raw`.

Confirm that ROS 2 receives a message:

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge run --rm \
  klass_ros1_bridge ros2 topic echo /imu_raw --once
```

```bash
docker compose -f compose.ros1_bridge.yml --profile bridge run --rm \
  klass_ros1_bridge ros2 topic echo /points_raw --flow-style --once
```

## Stop everything

```bash
docker stop klass_corridor_player klass_roscore klass_zenoh_router
docker compose -f compose.ros1_bridge.yml --profile bridge down
```
