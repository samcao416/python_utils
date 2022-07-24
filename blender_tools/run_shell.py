import os
import glob
import datetime


def check_images(root_dir, index):
    image_list = []
    image_dir = os.path.join(root_dir, "test_blender", "outputs", "No_%04d" %(index))
    image_list += glob.glob(os.path.join(image_dir, "images", "*.png"))
    image_num = len(image_list)
    return image_num

root_dir = "/media/stereye/新加卷/Sam/car_models/"

current_time = datetime.datetime.now()
log_file = os.path.join(root_dir, 'log_run_shell_%s.txt' %(current_time.strftime("%m_%d_%H_%M")))


with open(log_file, 'w') as f:
    print("Start Time: %s" %(str(current_time)), file = f)

print("Searching for .fbx files in \033[0;33;40m %s\033[0m" %(root_dir))

dir_dict = os.walk(root_dir)

fbx_path_list = []
for dirpath, dirnames, file_names in dir_dict:
    for dirname in dirnames:
        fbx_path = glob.glob(os.path.join(dirpath, dirname, "*.fbx"))
        fbx_path_list += fbx_path


# with open(os.path.join(root_dir,"fbx_list"), 'w') as f:
#     for fbx_path in fbx_path_list:
#         print(fbx_path, file=f)


print("\033[0;33;40m %d\033[0m .fbx files found." %(len(fbx_path_list)))
with open(log_file, 'a') as f:
    print("%d .fbx file found" %(len(fbx_path_list)), file = f)

for index, fbx_path in enumerate(fbx_path_list):
    print("\033[0;33;40m No.%04d: %s\033[0m" %(index, fbx_path))
    f = open(log_file, 'a')
    try:
        # os.system("blender -b -P test_blender_render.py -- \"%s\" %d" %(fbx_path, index))
        os.system("blender -b -P test_blender_flip_debug.py -- \"%s\" %d" %(fbx_path, index))
        image_num = check_images(root_dir, index)
        if image_num:
            print("No.%04d Success %04d Images Rendered. Path: %s" %(index, image_num, fbx_path), file = f)
        else:
            print("No.%04d Failed                        Path: %s" %(index, fbx_path), file = f)
    except:
        print("No.%04d Failed                        Path: %s" %(index, fbx_path), file = f)

    f.close()