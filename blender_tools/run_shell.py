import os
import glob
import datetime
import argparse
import numpy as np


def check_images(root_dir, index):
    image_list = []
    branches = ['z_up', 'z_x_180']
    for branch in branches:
        image_dir = os.path.join(root_dir, "outputs", "No_%04d" %(index), branch)
        image_list += glob.glob(os.path.join(image_dir, "images", "*.png"))
    image_num = len(image_list)
    return image_num

def search_ckpt(render_dir):
    dirs = sorted(os.listdir(render_dir))
    if dirs != []:
        end_index = int(dirs[-1][-4:])
    else:
        end_index = 0
    return end_index


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type = str, default="/media/stereye/新加卷/Sam/car_models/test_blender")
    parser.add_argument("--start", type = int, default = -1, help = "Input to start rendering from certain point")
    parser.add_argument("--end", type = int, default = -1, help = "Iuput to stop rendering at certain point")
    parser.add_argument("--clear", action = "store_true", help = "Input to clear all the output and start re-rendering")
    arg = parser.parse_args()
    # 0 142 284 426 568 710 852 994 1136

    root_dir = arg.path
    current_time = datetime.datetime.now()
    if not os.path.isdir(os.path.join(root_dir, 'outputs_no_bg_line')):
        os.makedirs(os.path.join(root_dir, 'outputs_no_bg_line'))
    log_file = os.path.join(root_dir, 'outputs_no_bg_line', 'log_run_shell_%04d_%04d_%s.txt' %(arg.start, arg.end, current_time.strftime("%m_%d_%H_%M")))
    

    ### The following code will find out all the .fbx files.
    if arg.clear or (not os.path.exists("fbx_path_list.npy")):

        with open(log_file, 'w') as f:
            print("Start Time: %s" %(str(current_time)), file = f)

        print("Searching for .fbx files in \033[0;33;40m %s\033[0m" %(root_dir))

        dir_dict = os.walk(root_dir)

        fbx_path_list = []
        for dirpath, dirnames, file_names in dir_dict:
            for dirname in dirnames:
                fbx_path = sorted(glob.glob(os.path.join(dirpath, dirname, "*.fbx")))
                fbx_path_list += fbx_path

        print("\033[0;33;40m %d\033[0m .fbx files found." %(len(fbx_path_list)))
        with open(log_file, 'a') as f:
            print("%d .fbx file found" %(len(fbx_path_list)), file = f)
        
        np.save("fbx_path_list.npy", fbx_path_list)
    else:
        fbx_path_list = list(np.load("fbx_path_list.npy"))
    
    if arg.start != -1:
        start_index = arg.start
    else:
        start_index = 0
    
    if (arg.end != -1) and arg.end <= len(fbx_path_list):
        end_index = arg.end
    else:
        end_index = len(fbx_path_list)
    
    if start_index >= end_index:
        raise RuntimeError("Wrong start and end index, please check again")

    # else:
    #     print("Searching for last breakpoint")
    #     start_index = search_ckpt(os.path.join(root_dir, "outputs_flips"))
    print("Starting rendering from\033[0;33;40m No.%04d \033[0m .fbx file." %(start_index))
    with open(log_file, 'a') as f:
        print("%s: Continue rendering from No.%04d" %(str(current_time), start_index))
        
    with open(log_file, 'a') as f:
        for index in range(start_index, end_index):
            fbx_path = fbx_path_list[index]
            print("\033[0;33;40m No.%04d: %s\033[0m" %(index, fbx_path))
            
            try:
                # os.system("blender -b -P test_blender_render.py -- \"%s\" %d" %(fbx_path, index))
                os.system("blender -b -P render_no_bg_line.py -- \"%s\" %d" %(fbx_path, index))
                image_num = check_images(root_dir, index)
                if image_num:
                    print("No.%04d Success %04d Images Rendered. Path: %s" %(index, image_num, fbx_path), file = f)
                else:
                    print("No.%04d Failed                        Path: %s" %(index, fbx_path), file = f)
            except:
                print("No.%04d Failed                        Path: %s" %(index, fbx_path), file = f)
