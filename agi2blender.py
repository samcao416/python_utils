from ctypes.wintypes import HACCEL
import numpy as np
import xml.etree.ElementTree as ET
import copy
import cv2
import os
import math
import json

source_dir = '.'
target_dir = '.'

scale = True

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

ext_xml = ET.ElementTree(file = os.path.join(source_dir, 'ext.xml'))

# Read intrinsic matrix

for elem in ext_xml.iter(tag = 'ImageDimensions'):
    dic = {}
    for i in elem.iter():
        dic[i.tag] = i.text
    width = float(dic['Width'])
    height = float(dic['Height'])

for i in ext_xml.iter(tag = 'FocalLengthPixels'):
    f = float(i.text)

for elem in ext_xml.iter(tag = 'PrincipalPoint'):
    dic = {}
    for i in elem.iter():
        dic[i.tag] = i.text
    cx = dic['x']
    cy = dic['y']

for elem in ext_xml.iter(tag = 'Distorsion'):
    dic = {}
    for i in elem.iter():
        dic[i.tag] = i.text
b1 = float(dic.get('B1', '0.0'))
b2 = float(dic.get('B2', '0.0'))
p1 = float(dic.get('P1', '0.0'))
p2 = float(dic.get('P2', '0.0'))
k1 = float(dic.get('K1', '0.0'))
k2 = float(dic.get('K2', '0.0'))
    


# Initalize the lines to write into the json file
angle_x = math.atan(width / (f * 2)) * 2
angle_y = math.atan(height / (f * 2)) * 2
AABB_SCALE = int(4)

out = {
        "camera_angle_x" : angle_x,
        "camera_angle_y" : angle_y,
        "fl_x" : f,
        "fl_y" : f,
        "k1" : k1,
        "k2" : k2,
        "p1" : p1,
        "p2" : p2,
        "b1" : b1,
        "b2" : b2,
        "cx" : cx, # + width / 2,
        "cy" : cy, # + height / 2,
        "w" : width,
        "h" : height,
        "aabb_scale" : AABB_SCALE,
        "frames" : [],
    }


# Read extrinsic matrix
c2ws = []
names = []

for elem in ext_xml.iter(tag = 'Photo'):
    dic = {}
    for i in elem.iter():
        dic[i.tag] = i.text
        if i.tag == 'Metadata':
            break

    name = str(dic['ImagePath'])
    name = 'images' + '/' + os.path.basename(name)
    
    M_00 = float(dic['M_00'])
    M_01 = float(dic['M_01'])
    M_02 = float(dic['M_02'])
    M_10 = float(dic['M_10'])
    M_11 = float(dic['M_11'])
    M_12 = float(dic['M_12'])
    M_20 = float(dic['M_20'])
    M_21 = float(dic['M_21'])
    M_22 = float(dic['M_22'])
    x = float(dic['x'])
    y = float(dic['y'])
    z = float(dic['z'])
    c2w = np.array([[M_00, -M_10, -M_20, x],
                   [M_01, -M_11, -M_21, y],
                   [M_02, -M_12, -M_22, z],
                   [0.  , 0.  , 0.  , 1.0]])
    names.append(name)
    c2ws.append(c2w)

c2ws = np.stack(c2ws, axis=0)
positions = c2ws[:, :3, 3] # (N, 3)
center = positions.mean(axis=0)
min_point = positions.min(axis=0)
max_point = positions.max(axis=0)

#print(min_point)
#print(max_point)

c2ws[:, :3, 3] = (c2ws[:, :3, 3] - center) / np.max(max_point-min_point) * 6
#c2ws[:, 2, 3] += 2

for i in range(len(names)):
    frame = {"file_path" : names[i], "transform_matrix" : c2ws[i]}
    out["frames"].append(frame)

#write json file
for f in out["frames"]:
    f["transform_matrix"] = f["transform_matrix"].tolist()
target_path = os.path.join(target_dir, "transforms.json")
print(f"writing {target_path}")
with open(target_path, "w") as outfile:
	json.dump(out, outfile, indent=2)