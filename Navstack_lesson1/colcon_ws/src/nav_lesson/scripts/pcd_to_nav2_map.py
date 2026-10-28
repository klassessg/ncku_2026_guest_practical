#!/workspace/lesson/venv/bin/python
"""Z-slice a PCD/PLY, project to 2D occupancy, save PGM and optional Nav2 map.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import open3d as o3d
except ImportError:
    o3d = None

# map_server / Nav2 trinary PGM (negate: 0): occupied=0, free=254, unknown=205
# https://wiki.ros.org/map_server#Map_Format
UNKNOWN = 205
FREE = 254
OCCUPIED = 0


def load_xyz(path: Path) -> np.ndarray:
    if o3d is None:
        raise SystemExit("open3d is required: pip install open3d")
    pcd = o3d.io.read_point_cloud(str(path))
    pts = np.asarray(pcd.points, dtype=np.float64)
    if pts.size == 0:
        raise ValueError(f"No points in {path}")
    return pts


def slice_z(points: np.ndarray, z_min: float, z_max: float) -> np.ndarray:
    if z_min > z_max:
        raise ValueError("z_min must be <= z_max")
    mask = (points[:, 2] >= z_min) & (points[:, 2] <= z_max)
    sliced = points[mask]
    if sliced.size == 0:
        raise ValueError(f"No points left after Z slice [{z_min}, {z_max}]")
    return sliced


def points_to_grid(
    points: np.ndarray,
    resolution: float,
    padding: float,
    mark_free: bool,
) -> tuple[np.ndarray, tuple[float, float, float]]:
    if resolution <= 0:
        raise ValueError("resolution must be > 0")

    x, y = points[:, 0], points[:, 1]
    x_min = float(x.min()) - padding
    x_max = float(x.max()) + padding
    y_min = float(y.min()) - padding
    y_max = float(y.max()) + padding

    width = int(np.ceil((x_max - x_min) / resolution))
    height = int(np.ceil((y_max - y_min) / resolution))
    if width < 1 or height < 1:
        raise ValueError("Invalid grid size")

    cols = np.floor((x - x_min) / resolution).astype(np.int64)
    rows = np.floor((y - y_min) / resolution).astype(np.int64)
    cols = np.clip(cols, 0, width - 1)
    rows = np.clip(rows, 0, height - 1)

    img = np.full((height, width), UNKNOWN, dtype=np.uint8)
    img[rows, cols] = OCCUPIED
    if mark_free:
        img[img == UNKNOWN] = FREE

    img = np.flipud(img)
    origin = (x_min, y_min, 0.0)
    return img, origin


def write_pgm(path: Path, image: np.ndarray) -> None:
    if image.dtype != np.uint8 or image.ndim != 2:
        raise ValueError("image must be 2D uint8")
    h, w = image.shape
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(f"P5\n{w} {h}\n255\n".encode("ascii"))
        f.write(image.tobytes())


def write_nav2_map(
    out_dir: Path,
    image: np.ndarray,
    resolution: float,
    origin: tuple[float, float, float],
    *,
    occupied_thresh: float = 0.65,
    free_thresh: float = 0.196,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pgm_path = out_dir / "map.pgm"
    yaml_path = out_dir / "map.yaml"
    write_pgm(pgm_path, image)
    ox, oy, oz = origin
    yaml_text = (
        "image: map.pgm\n"
        f"resolution: {resolution}\n"
        f"origin: [{ox}, {oy}, {oz}]\n"
        f"negate: 0\n"
        f"occupied_thresh: {occupied_thresh}\n"
        f"free_thresh: {free_thresh}\n"
    )
    yaml_path.write_text(yaml_text, encoding="utf-8")
    return pgm_path, yaml_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Slice PCD by Z, project to 2D, save PGM (and optional Nav2 map pair)."
    )
    parser.add_argument("input", type=Path, help="Input .pcd or .ply")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output .pgm (without --nav2-map-dir)")
    parser.add_argument("--nav2-map-dir", type=Path, default=None, help="Write map.pgm and map.yaml here")
    parser.add_argument("--z-min", type=float, required=True, help="Min Z (m)")
    parser.add_argument("--z-max", type=float, required=True, help="Max Z (m)")
    parser.add_argument("--resolution", type=float, default=0.05, help="Meters per pixel")
    parser.add_argument("--padding", type=float, default=0.5, help="Border padding (m)")
    parser.add_argument(
        "--mark-free",
        action="store_true",
        help="Set non-occupied cells to free (254) instead of unknown (205)",
    )
    args = parser.parse_args(argv)

    if args.nav2_map_dir is None and args.output is None:
        parser.error("Specify --nav2-map-dir and/or -o/--output")

    points = load_xyz(args.input)
    points = slice_z(points, args.z_min, args.z_max)
    img, origin = points_to_grid(
        points,
        resolution=args.resolution,
        padding=args.padding,
        mark_free=args.mark_free,
    )

    if args.nav2_map_dir is not None:
        pgm_path, yaml_path = write_nav2_map(
            args.nav2_map_dir,
            img,
            args.resolution,
            origin,
        )
        print(f"Wrote {pgm_path} ({img.shape[1]}x{img.shape[0]} px)")
        print(f"Wrote {yaml_path}")
        print(f"origin: [{origin[0]:.6f}, {origin[1]:.6f}, {origin[2]:.6f}]")

    if args.output is not None:
        write_pgm(args.output, img)
        print(f"Wrote {args.output} ({img.shape[1]}x{img.shape[0]} px)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
