#!/usr/bin/env bash
# Source before launching gz sim).

RESOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/gazebo_resources"
SMALL_HOUSE="${RESOURCE_DIR}/worlds/small_house"

export GZ_SIM_RESOURCE_PATH="${SMALL_HOUSE}:${SMALL_HOUSE}/models:${GZ_SIM_RESOURCE_PATH}"
echo "GZ_SIM_RESOURCE_PATH includes small_house at ${SMALL_HOUSE}"

ROBOT_RESOURCE_PATH="${RESOURCE_DIR}/robots"
export GZ_SIM_RESOURCE_PATH="${ROBOT_RESOURCE_PATH}:${GZ_SIM_RESOURCE_PATH}"
echo "Adding resource path for robots at ${ROBOT_RESOURCE_PATH}"

export TURTLEBOT3_MODEL=burger
echo "TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL}"
