import imageio
import numpy as np
import os
import glob
import cv2

dir = "./4k"
out_dir = os.path.join(dir, "croped")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

img_pth_ls = glob.glob(os.path.join(dir, '*.jpg'))

for img_pth in img_pth_ls:
    #img = np.array(imageio.imread(img_pth))
    img = cv2.imread(img_pth)
    img_croped = img[132:-132,648:-648]
    img_croped = cv2.resize(img_croped, [800,800])
    img_save_dir = os.path.join(out_dir, os.path.basename(img_pth))
    cv2.imwrite(img_save_dir, img_croped)