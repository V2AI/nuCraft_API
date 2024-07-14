import argparse
import os

import numpy as np
import open3d as o3d
from nuscenes.nuscenes import NuScenes
from nuscenes.utils.color_map import get_colormap

from efg.data.datasets.nuscenes.utils import read_file

if __name__ == "__main__":

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Example code to load and visualize the nuCraft data.")
    parser.add_argument("--data_root", required=True, help="The root directory of the data.")
    parser.add_argument("--lidar_token", required=True, help="The name of the sequence to process.")

    args = parser.parse_args()

    nusc = NuScenes(version='v1.0-trainval', dataroot='/path/to/your/nuScenes/dataroot/', verbose=True)

    idx2name = nusc.lidarseg_idx2name_mapping
    name2color = get_colormap()
    # brigh idx2color mapping
    idx2color_map = {idx: name2color[name] for idx, name in idx2name.items()}
    max_key = max(idx2color_map.keys())
    idx2color = np.array([idx2color_map.get(i, None) for i in range(max_key + 1)]) / 255.0

    data_root = args.data_root
    lidar_token = args.lidar_token

    lidar_data = nusc.get("sample_data", lidar_token)
    lidar_path = os.path.join(nusc.dataroot, nusc.get("sample_data", "b051c5282e7642b78cc73403a32c5875")["filename"])
    points = read_file(lidar_path)[:, :3]
    raw_pcd = o3d.geometry.PointCloud()
    raw_pcd.points = o3d.utility.Vector3dVector(points)

    data_path = args.lidar_token + ".bin"
    data = np.fromfile(os.path.join(data_root, data_path), dtype=np.int16).reshape(-1, 4)
    occ_origin = np.array([-51.15, -51.15, -4.95]).reshape(-1, 3)
    occ_centers = data[:, :3]  # X, Y, Z: 0-1023, 0-1023, 0-79
    occ_labels = data[:, -1]  # 0-31

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(occ_centers)
    pcd.colors = o3d.utility.Vector3dVector(idx2color[occ_labels])
    o3d.visualization.draw_geometries([raw_pcd, pcd])
