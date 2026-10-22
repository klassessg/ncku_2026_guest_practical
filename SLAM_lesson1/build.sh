#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker build -t klass_slam_lesson1 .
