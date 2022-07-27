import os
import argparse
import glob
import datetime
import numpy as np

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type = str, default="/media/stereye/新加卷/Sam/car_models/test_blender")
    parser.add_argument("--groups", type = int, default = 2, help = "the number of groups that fbx files will be devided into")
    parser.add_argument("--clear", action = "store_true", help = "Input to clear all the output and start re-rendering")
    arg = parser.parse_args()

    root_dir = arg.path
    current_time = datetime.datetime.now()
    log_file = os.path.join(root_dir, "log_run_%s.txt" %(current_time.strftime("%m_%d_%H_%M")))
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

    fbx_num = len(fbx_path_list)
    group_num = arg.groups
    group_member_num = round(fbx_num / group_num)
    index_list = []
    for i in range(group_num):
        index_list.append(i * group_member_num)
    index_list.append(fbx_num)
    for i in range(group_num):
        # os.system("gnome-terminal -- zsh -c \"python\"")
        # os.system("gnome-terminal -- bash -c \"python test_bash.py --start %d --end %d; exec bash;\"" %(index_list[i], index_list[i+1]))
        os.system("gnome-terminal -- bash -c \"python run_shell.py --start %d --end %d; exec bash;\"" %(index_list[i], index_list[i+1]))
        # os.system("python run_shell.py --start %d --end %d &" %(index_list[i], index_list[i+1]))
