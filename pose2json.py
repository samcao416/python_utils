import numpy as np
import json
import os
import math
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

folder = "/sharedata/home/caojm/datasets/IndoorDataFromLWT"
OUT_PATH = "/sharedata/home/caojm/datasets/IndoorDataFromLWT/transforms_part.json"
AABB_SCALE = int(16)
start_id = [2]
end_id = [369]

K_dir = os.path.join(folder, 'calibration.txt')
pose_dir = os.path.join(folder, 'ba_out.txt')

resize_scale = 1
w = float(4096) / resize_scale
h = float(3072) / resize_scale
fl_x = float(1921.739257812) / resize_scale
fl_y = float(1921.557373047) / resize_scale
k1 = 0
k2 = 0
p1 = 0
p2 = 0
cx = float(2039.995361328) / resize_scale
cy = float(1552.995361328) / resize_scale
angle_x = math.atan(w / (fl_x * 2)) * 2
angle_y = math.atan(h / (fl_y * 2)) * 2
fovx = angle_x * 180 / math.pi
fovy = angle_y * 180 / math.pi

with open(pose_dir, "r") as f:
    i = 1
    bottom = np.array([0.0, 0.0, 0.0, 1.0])
    out = {
			"camera_angle_x": angle_x,
			"camera_angle_y": angle_y,
			"fl_x": fl_x,
			"fl_y": fl_y,
			"k1": k1,
			"k2": k2,
			"p1": p1,
			"p2": p2,
			"cx": cx,
			"cy": cy,
			"w": w,
			"h": h,
			"aabb_scale": AABB_SCALE,
			"frames": [],
		}

    for line in f:
        if i % 4 == 1:
            name = "images/" + str(np.array(line.strip('\n').split(' ')).astype(np.int16)[0]) + ".jpg"
            idx = np.array(line.strip('\n').split(' ')).astype(np.int16)[0]
            c2w = []
        else:
            if (idx >= start_id[0] and idx <= end_id[0]):
                pose_line = np.array(line.strip('\n').split(' ')).astype(np.float16)
                if i % 4 == 0:
                    c2w.append(pose_line)
                    c2w.append(bottom)
                    c2w = np.array(c2w)
                    frame={"file_path":name,"transform_matrix": c2w}
                    out["frames"].append(frame)

                else:
                    c2w.append(pose_line)
        i += 1
nframes = len(out["frames"])
'''
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
print(totp) # the cameras are looking at totp
for f in out["frames"]:
	f["transform_matrix"][0:3,3] -= totp

avglen = 0.
for f in out["frames"]:
    avglen += np.linalg.norm(f["transform_matrix"][0:3,3])
avglen /= nframes
print("avg camera distance from origin", avglen)
for f in out["frames"]:
    f["transform_matrix"][0:3,3] *= 4.0 / avglen # scale to "nerf sized"
'''
for f in out["frames"]:
    f["transform_matrix"] = f["transform_matrix"].tolist()
print(nframes,"frames")

print(f"writing {OUT_PATH}")
with open(OUT_PATH, "w") as outfile:
	json.dump(out, outfile, indent=2)