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

# IF you want to use different SLAM algorithm, you can add them here to have it built into 
# the docker image

# Install SLAM Toolbox and map server for saving maps
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-slam-toolbox \
        ros-${ROS_DISTRO}-nav2-map-server \
    && rm -rf /var/lib/apt/lists/*

# Install open source SLAM algorithm
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-perception-pcl \
        ros-${ROS_DISTRO}-pcl-msgs \
        ros-${ROS_DISTRO}-pcl-conversions \
        ros-${ROS_DISTRO}-vision-opencv \
        ros-${ROS_DISTRO}-cv-bridge \
        ros-${ROS_DISTRO}-xacro \
        ros-${ROS_DISTRO}-gtsam \
        ros-${ROS_DISTRO}-tf2-eigen \
        ros-${ROS_DISTRO}-tf2-sensor-msgs \
        ros-${ROS_DISTRO}-tf2-geometry-msgs \
        libeigen3-dev \
        libpcl-dev \
        libopencv-dev \
        libomp-dev \
        libjsoncpp-dev \
        pcl-tools \
    && rm -rf /var/lib/apt/lists/*

# RTAB-Map 3D lidar odometry, graph SLAM and its native visualizer.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-imu-filter-madgwick \
        ros-${ROS_DISTRO}-rtabmap-odom \
        ros-${ROS_DISTRO}-rtabmap-slam \
        ros-${ROS_DISTRO}-rtabmap-viz \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/library_ws/src
RUN git clone https://github.com/tenvinc/LIO-SAM.git -b ros2-dev /workspace/library_ws/src/LIO-SAM
RUN apt-get update && rosdep install --from-paths /workspace/library_ws/src --ignore-src -y
RUN bash -c ". /opt/ros/${ROS_DISTRO}/setup.bash \
    && cd /workspace/library_ws \
    && export CMAKE_BUILD_PARALLEL_LEVEL=1 MAKEFLAGS=-j1 \
    && colcon build --parallel-workers 1 --cmake-args -DBUILD_TESTING=OFF"
    
# Setting things up so that workspace remains clean of build artifacts
RUN mkdir -p /workspace/lesson/colcon_ws
COPY ./colcon_ws/src /workspace/lesson/src
RUN ln -s /workspace/lesson/src /workspace/lesson/colcon_ws/src
RUN bash -c ". /opt/ros/${ROS_DISTRO}/setup.bash \
    && cd /workspace/lesson/colcon_ws \
    && export CMAKE_BUILD_PARALLEL_LEVEL=1 MAKEFLAGS=-j1 \
    && colcon build --parallel-workers 1"

RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc
RUN echo "source /workspace/library_ws/install/setup.bash" >> /root/.bashrc
RUN echo "source /workspace/lesson/colcon_ws/install/setup.bash" >> /root/.bashrc

WORKDIR /workspace/lesson/colcon_ws
CMD ["bash"]
