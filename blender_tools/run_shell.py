import os
import glob

root_dir = "/media/stereye/新加卷/Sam/car_models/"

print("Searching for .fbx files in \033[0;33;40m %s\033[0m" %(root_dir))

dir_dict = os.walk(root_dir)

fbx_path_list = []
for dirpath, dirnames, file_names in dir_dict:
    for dirname in dirnames:
        fbx_path = glob.glob(os.path.join(dirpath, dirname, "*.fbx"))
        fbx_path_list += fbx_path

print("\033[0;33;40m %d\033[0m .fbx files found." %(len(fbx_path_list)))

for index, fbx_path in enumerate(fbx_path_list):
    print("\033[0;33;40m No.%04d: %s\033[0m" %(index, fbx_path))
    os.system("blender -b -P test_blender_2.py -- \"%s\" %d" %(fbx_path, index))