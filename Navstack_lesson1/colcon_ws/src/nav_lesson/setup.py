from glob import glob
from os.path import join

from setuptools import setup

package_name = "nav_lesson"

def _map_files() -> list[str]:
    patterns = ("*.pcd", "*.pgm", "*.yaml")
    files: list[str] = []
    for pattern in patterns:
        files.extend(glob(join("maps", "small_house", pattern)))
    return sorted(set(files))


setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (join("share", package_name, "launch"), glob("launch/*.py")),
        (join("share", package_name, "config"), glob("config/*")),
        (join("share", package_name, "maps", "small_house"), _map_files()),
        (join("share", package_name, "urdf"), glob("urdf/*")),
        (join("share", package_name, "rviz"), glob("rviz/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="NCKU Navstack Lesson",
    maintainer_email="lesson@example.com",
    description="Minimal Nav2 bringup for Navstack lesson 1",
    license="Apache-2.0",
)
