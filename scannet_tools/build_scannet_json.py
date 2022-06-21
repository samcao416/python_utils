from errno import EMULTIHOP
import numpy as np
import os
import argparse

import sys
sys.path.append("..")

from scannet_tools.utils.SensorData import SensorData
from scannet_tools.utils.scannet_function import pose_transformation, pose_original
from scannet_tools.utils.image_process import check_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type = str, default='/media/stereye/新加卷/Sam/linux_files/scannet')
    parser.add_argument('--scene', type = int, default = 0)
    parser.add_argument('--group', type = int, default = 0)
    parser.add_argument('--build_new', action = "store_true")
    parser.add_argument('--transform', action = "store_true", help='whether add transformations on oringal poses')
    parser.add_argument('--blur_filt', action = "store_true")
    parser.add_argument('--start', type = int ,default=0)
    parser.add_argument('--end', type = int, default=-1)
    parser.add_argument('--step', type = int, default = 1)
    arg = parser.parse_args()

    scene_full_name = "scene%04d_%02d" % (arg.scene, arg.group)
    branches = []

    if arg.build_new:
        
        sens_path = os.path.join(arg.path, "downloads", "scans", scene_full_name, "%s.sens" % scene_full_name)
        
        output_path = os.path.join(arg.path, "data_new", "scans", scene_full_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        sd = SensorData(sens_path)
        sd.export_color_images(os.path.join(output_path, 'color'))
        sd.export_depth_images(os.path.join(output_path, 'depth'))
        sd.export_intrinsics(os.path.join(output_path, 'intrinsic'))
        sd.export_poses(os.path.join(output_path, 'pose'))
        branches.append("data_new")
    
    branches.append("data")
    #splits = ["color", "depth", "intrinsic", "pose"]


    process_poses = pose_transformation if arg.transform else pose_original

    for branch in branches:
        root_dir = os.path.join(arg.path, branch, "scans", scene_full_name)
        print(print("------processing %s----------" %root_dir))
        '''
        scene0000_00:
            color:
                0.jpg
                1.jpg
                ...
            depth:
                0.png
                1.png
                ...
            intrinsic:
                intrinsic_depth.txt -> 4*4 matrix
                intrinsic_color.txt -> 4*4 matrix
                extrinsic_depth.txt -> identity matrix, useless
                extrinsic_color.txt -> identity matirx, useless
            pose:
                0.txt -> 4*4 matrix
                1.txt
                ...
        '''
        crop_or_not, blur_value_dict = check_image(root_dir)

        process_poses(root_dir, blur_value_dict, start = arg.start, end = arg.end, crop_or_not = crop_or_not, filt_or_not=arg.blur_filt)


        
        print("json file saved.")