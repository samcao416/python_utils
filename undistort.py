'''
This script is used to undistort fisheye images
You need to change camera intrinsics and paths by yourself

Reqirements:
conda install -c conda-forge opencv
pip install tqdm
'''


import cv2
import numpy as np
import tqdm
import os
import glob

#skip_line = 0
#with open('./pinhole-equi-512/cambine-imucam-imucalib.yaml') as infile:
f = 856.834205
cx = -22.9639 + 1440
cy = 19.2354 + 1440
k1 = 0.0217334
k2 = -0.00347387
k3 = -0.0011752
k4 = -0.000147514
K = np.array([[f,0,cx],[0,f,cy],[0,0,1]])
K_new = np.array([[f/1.2,0,cx],[0,f/1.2,cy],[0,0,1]])
D = np.array([k1, k2, k3, k4])

DIM = [2880, 2880]

#img = cv2.imread("./VID_20220318_140633_00_006_back.mp4image/ 340.jpg", cv2.IMREAD_UNCHANGED)
#print(img.shape)
#undistorted_img = cv2.fisheye.undistortImage(img,K,D,Knew = K, new_size = DIM)
#cv2.imwrite("D:/Sam/insta360/0318/VID_20220318_140633_00_006_back.mp4image/340_out.jpg", undistorted_img)
source_dir = "D:/Sam/insta360/0318/VID_20220318_140633_00_006_back.mp4image"
output_dir = "D:/Sam/insta360/0318/undistorted/VID_20220318_140633_00_006_back.mp4image"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

img_path_list = sorted(glob.glob(os.path.join(source_dir, '*.jpg')))

for img_path in tqdm.tqdm(img_path_list):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    undistorted_img = cv2.fisheye.undistortImage(img,K,D,Knew = K, new_size = DIM)
    output_path = os.path.join(output_dir, os.path.basename(img_path))
    cv2.imwrite(output_path, undistorted_img)