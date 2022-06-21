import cv2
import numpy as np
import os
import json
import glob
import imageio
import math

def sharpness(imagePath):
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	fm = variance_of_laplacian(gray)
	return fm

def variance_of_laplacian(image):
	return cv2.Laplacian(image, cv2.CV_64F).var()

def rotmat(a, b):
	a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
	v = np.cross(a, b)
	c = np.dot(a, b)
	s = np.linalg.norm(v)
	kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
	return np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2 + 1e-10))

def closest_point_2_lines(oa, da, ob, db): # returns point closest to both rays of form o+t*d, and a weight factor that goes to 0 if the lines are parallel
	da = da / np.linalg.norm(da)
	db = db / np.linalg.norm(db)
	c = np.cross(da, db)
	denom = np.linalg.norm(c)**2
	t = ob - oa
	ta = np.linalg.det([t, db, c]) / (denom + 1e-10)
	tb = np.linalg.det([t, da, c]) / (denom + 1e-10)
	if ta > 0:
		ta = 0
	if tb > 0:
		tb = 0
	return (oa+ta*da+ob+tb*db) * 0.5, denom    

def pose_transformation(root_dir, blur_value_dict, start= 0, end = -1, step =1, crop_or_not = False, filt_or_not = False):
    if crop_or_not:
        color_path = os.path.join(root_dir, 'cropped')
    else:
        color_path = os.path.join(root_dir, 'color')
    #depth_path = os.path.join(root_dir, 'depth')
    intrinsic_path = os.path.join(root_dir, 'intrinsic')
    pose_path = os.path.join(root_dir, 'pose')


    # load intrinsics
    intrinsic_file = os.path.join(intrinsic_path, 'intrinsic_color.txt')
    image_example = os.path.join(color_path, '0.jpg')
    if not os.path.isfile(intrinsic_file):
        raise RuntimeError("No intrinsic_color.txt")
    if not os.path.isfile(image_example):
        raise RuntimeError("No 0.jpg")
    else:
        image_0 = imageio.imread(image_example)
        w = image_0.shape[0]
        h = image_0.shape[1]
    
    with open(intrinsic_file) as f:
        intri = np.loadtxt(f)
    
    fl_x = intri[0,0] 
    fl_y = intri[1,1]
    if crop_or_not:
        cx = intri[0,2] - 20
        cy = intri[1,2] - 20
    else:
        cx = intri[0,2]
        cy = intri[1,2]
    # wait k1
    k1 = 0
    k2 = 0
    p1 = 0
    p2 = 0
    b1 = 0
    b2 = 0
    angle_x = math.atan(w / (fl_x * 2)) * 2
    angle_y = math.atan(h / (fl_y * 2)) * 2
    
    #prepare output json dict
    out = {
        "camera_angle_x": angle_x,
        "camera_angle_y": angle_y,
        "fl_x": fl_x,
        "fl_y": fl_y,
        "k1": k1,
        "k2": k2,
        "p1": p1,
        "p2": p2,
        "b1": b1,
        "b2": b2,
        "cx": cx,
        "cy": cy,
        "w": w,
        "h": h,
        "aabb_scale": 8,
        "frames": [],
        }

    # # load poses
    # path_file_list = sorted(glob.glob(os.path.join(pose_path, "*.txt")), key = lambda x:int(os.path.basename(x)[0:-4]))
    # if len(path_file_list) == 0:
    #     raise RuntimeError("No pose txt file found. Please check again")
    # poses = []

    # path_file_list = path_file_list[start:end:step]
    # for path_file in path_file_list:
    #     with open(path_file) as f:
    #         pose = np.loadtxt(f)
    #     poses.append(pose)
    # poses = np.stack(poses, axis = 0) # N, 4, 4

    # # write poses to json dict
    # img_files_list = sorted(glob.glob(os.path.join(color_path, "*.jpg")), key = lambda x:int(os.path.basename(x)[0:-4]))
    # #img_files_list = img_files_list[::step]
    # img_files_list = img_files_list[start:end:step]

        # load poses
    pose_file_list = sorted(glob.glob(os.path.join(pose_path, "*.txt")), key = lambda x:int(os.path.basename(x)[0:-4]))
    if len(pose_file_list) == 0:
        raise RuntimeError("No pose txt file found. Please check again")
    img_path_list = sorted(glob.glob(os.path.join(color_path, "*.jpg")), key = lambda x:int(os.path.basename(x)[0:-4]))
    
    if len(pose_file_list) != len(img_path_list):
        raise RuntimeError("The number of poses does not match the number of images")

    if filt_or_not:
        blur_thres = blur_value_dict['blur_thres']
    else:
        blur_thres = 2.0

    poses = []

    img_files_list = []

    for i in range(start, end, step):
        blurness = blur_value_dict['frames'][i]['blur_extent']
        if blurness > blur_thres:
            continue
        pose_file = pose_file_list[i]
        with open(pose_file, 'r') as f:
            pose = np.loadtxt(f)
        if np.math.isnan(np.sum(pose)):
            continue
        poses.append(pose)
        img_files_list.append(img_path_list[i])
    poses = np.stack(poses, axis = 0)


    up = np.zeros(3).astype(np.float32)
    for i, pose in enumerate(poses):
        name = img_files_list[i]

        b = sharpness(name)

        c2w = pose
        c2w[0:3, 2] *= -1
        c2w[0:3, 1] *= -1
        #c2w = c2w[[1, 0,2,3],:]

        
        if np.math.isinf(np.sum(c2w)) or np.math.isnan(np.sum(c2w)):
            print("Abnormal value: ",i, c2w)
            continue
            # print(c2w)
            # input()
            # input()
        up += c2w[0:3, 1]

        if crop_or_not:
            folder_name = "cropped"
        else:
            folder_name = "color"
        frame = {"file_path": os.path.join(folder_name,os.path.basename(img_files_list[i])), "sharpness": b, "transform_matrix":pose}        
        out["frames"].append(frame)

    nframes = len(out["frames"])
    up = up / np.linalg.norm(up) 
    print("up vector was", up)
    R = rotmat(up,[0,0,1]) # rotate up vector to [0,0,1]
    R = np.pad(R,[0,1])
    R[-1, -1] = 1



    for f in out["frames"]:
        f["transform_matrix"] = np.matmul(R, f["transform_matrix"]) # rotate up to be the z axis

    # find a central point they are all looking at
    print("computing center of attention...")

    totw = 0.0
    totp = np.array([0.0, 0.0, 0.0])
    for f in out["frames"]:
        mf = f["transform_matrix"][0:3,:]
        for g in out["frames"]:
            mg = g["transform_matrix"][0:3,:]
            p, w = closest_point_2_lines(mf[:,3], mf[:,2], mg[:,3], mg[:,2])
            if w > 0.01:
                totp += p*w
                totw += w

    totp /= totw
    if totw == 0:
        totp = np.array([0.0, 0.0, 0.0])
        for f in out["frames"]:
            totp += f["transform_matrix"][0:3,3] 
        totp = totp/ nframes        
    print(totp) 
    print(totp) # the cameras are looking at totp
    for f in out["frames"]:
        f["transform_matrix"][0:3,3] -= totp
        # print(f["transform_matrix"])
    avglen = 0.
    for f in out["frames"]:
        avglen += np.linalg.norm(f["transform_matrix"][0:3,3])
    avglen /= nframes
    avglen_scale = 1.0/8.0
    print("avg camera distance from origin", avglen)
    for f in out["frames"]:
        f["transform_matrix"][0:3,3] *= avglen_scale / avglen # scale to "nerf sized"
    out["scale"] = avglen_scale / avglen
    for f in out["frames"]:
        f["transform_matrix"] = f["transform_matrix"].tolist()

    #write json files

    target_path = os.path.join(root_dir, "transforms_transformed.json")

    print(f"writing {target_path}")

    with open(target_path, 'w') as outfile:
        json.dump(out, outfile, indent = 2)

    pass

def pose_original(root_dir, blur_value_dict, start = 0, end = 0, step = 1, crop_or_not = False, filt_or_not = False):
    if crop_or_not:
        color_path = os.path.join(root_dir, 'cropped')
    else:
        color_path = os.path.join(root_dir, 'color')
    intrinsic_path = os.path.join(root_dir, 'intrinsic')
    pose_path = os.path.join(root_dir, 'pose')

    # load intrinsics
    intrinsic_file = os.path.join(intrinsic_path, 'intrinsic_color.txt')
    image_example = os.path.join(color_path, '0.jpg')
    if not os.path.isfile(intrinsic_file):
        raise RuntimeError("No intrinsic_color.txt")
    if not os.path.isfile(image_example):
        raise RuntimeError("No 0.jpg")
    else:
        image_0 = imageio.imread(image_example)
        w = image_0.shape[0]
        h = image_0.shape[1]

    with open(intrinsic_file) as f:
        intri = np.loadtxt(f)
    
    fl_x = intri[0,0]
    fl_y = intri[1,1]
    if crop_or_not:
        cx = intri[0,2] - 20 # defautly the image is croped 20 pixels each side
        cy = intri[1,2] - 20
    else:
        cx = intri[0,2]
        cy = intri[1,2]
    # wait k1
    k1 = 0
    k2 = 0
    p1 = 0
    p2 = 0
    b1 = 0
    b2 = 0
    angle_x = math.atan(w / (fl_x * 2)) * 2
    angle_y = math.atan(h / (fl_y * 2)) * 2

    #prepare output json dict
    out = {
        "camera_angle_x": angle_x,
        "camera_angle_y": angle_y,
        "fl_x": fl_x,
        "fl_y": fl_y,
        "k1": k1,
        "k2": k2,
        "p1": p1,
        "p2": p2,
        "b1": b1,
        "b2": b2,
        "cx": cx,
        "cy": cy,
        "w": w,
        "h": h,
        "aabb_scale": 8,
        "frames": [],
        }

    # load poses
    pose_file_list = sorted(glob.glob(os.path.join(pose_path, "*.txt")), key = lambda x:int(os.path.basename(x)[0:-4]))
    if len(pose_file_list) == 0:
        raise RuntimeError("No pose txt file found. Please check again")
    img_path_list = sorted(glob.glob(os.path.join(color_path, "*.jpg")), key = lambda x:int(os.path.basename(x)[0:-4]))
    
    if len(pose_file_list) != len(img_path_list):
        raise RuntimeError("The number of poses does not match the number of images")

    if filt_or_not:
        blur_thres = blur_value_dict['blur_thres']
    else:
        blur_thres = 2.0

    poses = []

    img_files_list = []

    for i in range(start, end, step):
        blurness = blur_value_dict['frames'][i]['blur_extent']
        if blurness > blur_thres:
            continue
        pose_file = pose_file_list[i]
        with open(pose_file, 'r') as f:
            pose = np.loadtxt(f)
        if np.math.isnan(np.sum(pose)):
            continue
        poses.append(pose)
        img_files_list.append(img_path_list[i])
    poses = np.stack(poses, axis = 0)
        

    # path_file_list = path_file_list[start:end:step]
    # for path_file in path_file_list:
    #     with open(path_file) as f:
    #         pose = np.loadtxt(f)
    #     poses.append(pose)
    # poses = np.stack(poses, axis = 0) # N, 4, 4

    # write poses to json dict
    # img_files_list = sorted(glob.glob(os.path.join(color_path, "*.jpg")), key = lambda x:int(os.path.basename(x)[0:-4]))
   
    # img_files_list = img_files_list[start:end:step]

    positions = poses[:, :3, 3]
    center = np.mean(positions, axis = 0)
    min_point = np.min(positions, axis = 0)
    max_point = np.max(positions, axis = 0)

    poses[:, :3, 2] *= -1
    poses[:, :3, 1] *= -1

    resize_scale = 0.125 / np.max(max_point - min_point)

    poses[:,:3, 3]  =  (poses[:,:3, 3] - center) * resize_scale

    out["scale"] = resize_scale

    for i, pose in enumerate(poses):
        name = img_files_list[i]
        
        b = sharpness(name)

        if crop_or_not:
            folder_name = "cropped"
        else:
            folder_name = "color"
        frame = {"file_path": os.path.join(folder_name,os.path.basename(img_files_list[i])), "sharpness": b, "transform_matrix":pose}        
        out["frames"].append(frame)

    nframes = len(out["frames"])
    
    for f in out["frames"]:
        f["transform_matrix"] = f["transform_matrix"].tolist()

    target_path = os.path.join(root_dir, "transforms_original.json")

    print(f"writing {target_path}")

    with open(target_path, 'w') as outfile:
        json.dump(out, outfile, indent = 2)
