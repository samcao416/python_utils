import numpy as np
import cv2
import json
import os
import glob
import random
import pywt

def check_edge(image_path):
    image = cv2.imread(image_path)
    
    left = image[:,0,:]
    right = image[:,-1,:]
    up = image[0,:,:]
    down = image[-1,:,:]

    H = left.shape[0]
    W = up.shape[0]

    left_black_ratio = left[np.all(left < 15, axis = 1)].shape[0] / H
    right_black_ratio = right[np.all(right < 15, axis = 1)].shape[0] / H
    up_black_ratio = up[np.all(up < 15, axis = 1)].shape[0] / W
    down_black_ratio = down[np.all(down < 15, axis = 1)].shape[0] / W

    if left_black_ratio > 0.9 and right_black_ratio > 0.9 \
            and up_black_ratio > 0.9 and down_black_ratio > 0.9:
        return True
    else:
        return False



def non_overlapping_max_pooling(image, kernel_size, padding = False):
    '''
    Non-overlapping pooling on 2D or 3D image.
    :param image: ndarray, input image to pool.
    :param kernel_size: kernel size of int or tuple of 2 in (kH, kW).
    :param padding: bool, pad the input image or not
    :return: the max-pooled image
    '''

    H, W = image.shape[:2]
    kH, kW = kernel_size , kernel_size if isinstance(kernel_size, int) else int(kernel_size)

    _ceil = lambda x, y: int(np.ceil(x / float(y)))

    if padding:
        nH = _ceil(H, kH)
        nW = _ceil(W, kW)
        size = (nH * kH, nW * kW) + image.shape[2:]
        image_pad = np.full(size, np.nan)
        image_pad[:H, :W, ...] = image
    else:
        nH = H // kH
        nW = W // kW
        image_pad = image[:H // kH * kH, :W // kW * kW, ...]

    new_shape = (nH, kH, nW, kW) + image.shape[2:]
    return np.nanmax(image_pad.reshape(new_shape), axis = (1, 3))

def Haar_Wavelet_Filter(gray_img, threshold, kernel_size = 8):
    o_h, o_w = gray_img.shape

    # Crop input image to be dibisible by kernel size
    gray_img = gray_img[0:int(o_h / kernel_size) * kernel_size, 0:int(o_w / kernel_size) * kernel_size]

    # Step 1, compute Haar Wavelet of input image
    LL1, (LH1, HL1, HH1) = pywt.dwt2(gray_img, "haar")

    # Another application of 2D haar to LL1
    LL2, (LH2, HL2, HH2) = pywt.dwt2(LL1, "haar")

    # Another application of 2D haar to LL2
    LL3, (LH3, HL3, HH3) = pywt.dwt2(LL2, "haar")

    # Construct the edge map in each scale Step 2
    E1 = np.sqrt(np.power(LH1, 2) + np.power(HL1, 2) + np.power(HH1, 2))
    E2 = np.sqrt(np.power(LH2, 2) + np.power(HL2, 2) + np.power(HH2, 2))
    E3 = np.sqrt(np.power(LH3, 2) + np.power(HL3, 2) + np.power(HH3, 2))

    # Perform non-overlapping max pooling for each scale
    Emax1 = non_overlapping_max_pooling(E1, kernel_size, padding = True)
    Emax2 = non_overlapping_max_pooling(E2, kernel_size // 2, padding=True)
    Emax3 = non_overlapping_max_pooling(E3, kernel_size // 4, padding=True)

    # Step 3
    EdgePoint1 = Emax1 > threshold
    EdgePoint2 = Emax2 > threshold
    EdgePoint3 = Emax3 > threshold

    # Rule 1 Edge Points
    EdgePoint = np.logical_or.reduce((EdgePoint1, EdgePoint2, EdgePoint3))

    # Rule 2 Dirak-Structure or Astep-Structure
    DAstructure = np.logical_and(
        Emax1[EdgePoint] > Emax2[EdgePoint],
        Emax2[EdgePoint] > Emax3[EdgePoint]
    )

    # Rule 3 Roof-Structure of Gstep-Structure
    RGstructure = np.logical_and(
        Emax1[EdgePoint] < Emax2[EdgePoint],
        Emax2[EdgePoint] < Emax3[EdgePoint]
    )

    # Rule 4 Roof-Structure

    RSstructure = np.logical_and(
        Emax2[EdgePoint] > Emax1[EdgePoint],
        Emax2[EdgePoint] > Emax2[EdgePoint]
    )

    # Rule 5 Edge more likely to be in a blurred image
    BlurC = Emax1[EdgePoint][np.logical_or(RGstructure, RSstructure)] < threshold

    # Step 6
    Per = np.sum(DAstructure) / np.sum(EdgePoint)
    
    # Step 7
    if (np.sum(RGstructure) + np.sum(RSstructure)) == 0:
        BlurExtent = 1.

    else:
        BlurExtent = np.sum(BlurC) / (np.sum(RGstructure) + np.sum(RSstructure))

    return Per, BlurExtent

def find_blur_threshlod(blur_value_dict):
    for f in blur_value_dict['frames']:
        blurness.append(f['blur_extent'])
    blurness = np.stack(blurness, axis = 0)
    thres = blurness[int(blurness.shape[0]*0.125)]
    return thres


def check_image(root_dir):
    image_path_list = sorted(glob.glob(os.path.join(root_dir, 'color', '*.jpg')), key = lambda x: int(os.path.basename(x)[:-4]))

    edge_index = random.randint(0, len(image_path_list))
    crop_or_not =  check_edge(image_path_list[edge_index])
    img_list = []
    if crop_or_not:
        if not os.path.exists(os.path.join(root_dir, 'cropped')):
            os.makedirs(os.path.join(root_dir, 'cropped'))
        for image_path in image_path_list:
            img = cv2.imread(image_path) # H, W, BGR
            img_crop = img[20:-20, 20:-20, :]
            img_list.append(img_crop)
            img_crop_path = os.path.join(root_dir, 'cropped', os.path.basename(image_path))
            cv2.imwrite(img_crop_path, img_crop)
    else:
        for image_path in image_path_list:
            img = cv2.imread(image_path)
            img_list.append(img)


    blur_value_dict = {'blur_thres':0.0,'frames':[]}

    for i, img in enumerate(img_list):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        per, blurext = Haar_Wavelet_Filter(gray_img, threshold = 35, kernel_size = 16)
        blur_value_dict['frames'].append({'name':os.path.basename(image_path), 'per':per, 'blur_extent': blurext})
    
    blur_thres = find_blur_threshlod(blur_value_dict)
    blur_value_dict['blur_thres'] = blur_thres

    saving_path = os.path.join(root_dir, 'intrinsic', 'blurness_HW.json')
    with open(saving_path, 'w') as out_file:
        json.dump(blur_value_dict, out_file, indent = 2)
    
    return crop_or_not, blur_value_dict 