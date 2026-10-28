FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Etc/UTC

RUN apt-get update && apt-get upgrade -y

# Install the Zenoh middleware so that modules can communicate with each other
ENV RMW_IMPLEMENTATION=rmw_zenoh_cpp
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-rmw-zenoh-cpp \
    && rm -rf /var/lib/apt/lists/*

# Add additional method of visualization using foxglove
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-foxglove-bridge \
    && rm -rf /var/lib/apt/lists/*

# Nav2 navigation stack
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-navigation2 \
        ros-${ROS_DISTRO}-nav2-bringup \
        ros-${ROS_DISTRO}-nav2-minimal-tb3-sim \
        ros-${ROS_DISTRO}-xacro \
    && rm -rf /var/lib/apt/lists/*

# Gazebo Sim, ROS–Gazebo integration, and TB3 simulation assets.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-ros-gz \
        ros-${ROS_DISTRO}-ros-gz-sim \
        ros-${ROS_DISTRO}-ros-gz-bridge \
        ros-${ROS_DISTRO}-gz-sim-vendor \
        ros-${ROS_DISTRO}-turtlebot3-gazebo \
    && rm -rf /var/lib/apt/lists/*

# LIO-SAM (mapping) — Referenced from SLAM_lesson1
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-perception-pcl \
        ros-${ROS_DISTRO}-pcl-msgs \
        ros-${ROS_DISTRO}-pcl-conversions \
        ros-${ROS_DISTRO}-vision-opencv \
        ros-${ROS_DISTRO}-cv-bridge \
        ros-${ROS_DISTRO}-gtsam \
        ros-${ROS_DISTRO}-tf2-eigen \
        ros-${ROS_DISTRO}-tf2-sensor-msgs \
        ros-${ROS_DISTRO}-tf2-geometry-msgs \
        libeigen3-dev \
        libpcl-dev \
        libopencv-dev \
        libomp-dev \
        libjsoncpp-dev \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /workspace/library_ws/src
RUN git clone https://github.com/tenvinc/LIO-SAM.git -b ros2-dev /workspace/library_ws/src/LIO-SAM

# Install the localization stack
RUN git clone https://github.com/rsasaki0109/ndt_omp_ros2.git -b humble /workspace/library_ws/src/ndt_omp_ros2
RUN git clone https://github.com/rsasaki0109/lidar_localization_ros2.git -b jazzy /workspace/library_ws/src/lidar_localization_ros2
RUN apt-get update && rosdep install --from-paths /workspace/library_ws/src --ignore-src -y
RUN bash -c ". /opt/ros/${ROS_DISTRO}/setup.bash \
    && cd /workspace/library_ws \
    && export CMAKE_BUILD_PARALLEL_LEVEL=1 MAKEFLAGS=-j1 \
    && colcon build --parallel-workers 1 --cmake-args -DBUILD_TESTING=OFF"

# Install dependencies for pcd_to_nav2_map
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-venv \
        python3-pip \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /workspace/lesson/venv
RUN /workspace/lesson/venv/bin/pip install open3d numpy

RUN mkdir -p /workspace/lesson/colcon_ws
COPY ./colcon_ws/src /workspace/lesson/src
RUN ln -s /workspace/lesson/src /workspace/lesson/colcon_ws/src
RUN bash -c ". /opt/ros/${ROS_DISTRO}/setup.bash \
    && cd /workspace/lesson/colcon_ws \
    && export CMAKE_BUILD_PARALLEL_LEVEL=1 MAKEFLAGS=-j1 \
    && colcon build --parallel-workers 1 --cmake-args -DBUILD_TESTING=OFF"
COPY ./env.sh /workspace/lesson/env.sh

RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc
RUN echo "source /workspace/library_ws/install/setup.bash" >> /root/.bashrc
RUN echo "source /workspace/lesson/colcon_ws/install/setup.bash" >> /root/.bashrc
RUN echo "source /workspace/lesson/env.sh" >> /root/.bashrc

WORKDIR /workspace/lesson
CMD ["bash"]
