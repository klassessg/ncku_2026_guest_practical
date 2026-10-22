# NCKU 2026 Guest Practical

Hands-on ROS 2 robotics practicals:

- [SLAM_lesson1](SLAM_lesson1/Readme.md): LiDAR SLAM with LIO-SAM and RTAB-Map on recorded bags.
- [Navstack_lesson1](Navstack_lesson1/Readme.md): mapping, localization and Nav2 navigation with a simulated TurtleBot3.
- [ROS1_bridge.md](ROS1_bridge.md): bridging ROS 1 bags and nodes into ROS 2.

## Datasets and Licenses

The [SLAM lesson](SLAM_lesson1/Readme.md) uses two datasets. Each is used under its own license, listed below.
The licenses apply only to the data, not to the code and configs in this repository.

| Dataset | Bag used in the SLAM lesson | Source | License |
| --- | --- | --- | --- |
| KLASS GHOST MacPherson dataset | `ghost_macpherson_ros_imu` | KLASS (provided with the SLAM lesson) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| Newer College Dataset (Multi-Camera extension) | `2021-07-01-10-37-38-quad-easy` | [ori-drs / Newer College Dataset](https://ori-drs.github.io/newer-college-dataset/) | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

### KLASS GHOST MacPherson dataset

The GHOST MacPherson dataset was collected by KLASS with a Ghost Robotics
Vision60 quadruped and is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You may share and adapt the data for non-commercial purposes, provided that you
credit KLASS, indicate if changes were made, and distribute any derived data
under the same license.

### Newer College Dataset (third party)

The Newer College bag is **not** produced by KLASS. It is a third-party dataset
created by the [Dynamic Robot Systems group (ori-drs)](https://github.com/ori-drs)
at the Oxford Robotics Institute, University of Oxford.

- Project page: <https://ori-drs.github.io/newer-college-dataset/>
- Download page: <https://ori-drs.github.io/newer-college-dataset/download/>
- License: [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/), intended for non-commercial academic use

It is used in the SLAM lesson under that license, for non-commercial teaching only.
All credit for the data goes to the original authors. The terms on the original
project page take precedence over this summary. For commercial use, contact the
dataset authors as described on the project page.

If you use this data in your own work, please cite the original authors:

```bibtex
@misc{zhang2021multicamera,
  title         = {Multi-Camera LiDAR Inertial Extension to the Newer College Dataset},
  author        = {Zhang, Lintong and Camurri, Marco and Wisth, David and Fallon, Maurice},
  year          = {2021},
  eprint        = {2112.08854},
  archivePrefix = {arXiv},
  primaryClass  = {cs.RO}
}

@inproceedings{ramezani2020newer,
  title     = {The Newer College Dataset: Handheld LiDAR, Inertial and Vision with Ground Truth},
  author    = {Ramezani, Milad and Wang, Yiduo and Camurri, Marco and Wisth, David and Mattamala, Matias and Fallon, Maurice},
  booktitle = {2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
  pages     = {4353--4360},
  year      = {2020}
}
```
