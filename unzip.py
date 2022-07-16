import os
from pickle import GLOBAL
import zipfile39 as zipfile
import rarfile
import py7zr
import glob
from tqdm import tqdm
import numpy as np

global err_file_list

err_file_list = []

def un_zip(file_name):
    try:
        zip_file = zipfile.ZipFile(file_name)

        os.makedirs(file_name + '_extract')
        zip_file.extractall(file_name + '_extract')
        zip_file.close()
    except:
        err_file_list.append(file_name)
   

def un_rar(file_name):
    try:
        rar_file = rarfile.RarFile(file_name)
        os.makedirs(file_name + '_extract')

        rar_file.extractall(file_name + '_extract')
        rar_file.close()
    except:
        err_file_list.append(file_name)
    

def un_7z(file_name):
    try:
        z7_file = py7zr.SevenZipFile(file_name)

        os.makedirs(file_name + '_extract')

        z7_file.extractall(file_name + '_extract')
        z7_file.close()
    except:
        err_file_list.append(file_name)

    

# zip_file = "test/porsche-718-cayman-gt4-2020.zip"
# un_zip(zip_file)

# z7_file = "test/Mercedes-Benz C-Class 2019.7z"
# un_7z(z7_file)

# rar_file = "test/Car Porsche 911 Carrera Cabriolet 2019.rar"
# un_rar(rar_file)

dict_dir = os.walk('.')
# for dirpath, dirnames, filenames in os.walk('.'):
#     for dirname in dirnames:
#         print(os.path.join(dirpath, dirname))
# for dirpath, dirnames, filenames in os.walk('.'):
#     for filename in filenames:
#         print(os.path.join(dirpath, filename))

zip_file_list = []
rar_file_list = []
z7_file_list = []

for dirpath, dirnames, filenames in dict_dir:
    for dirname in dirnames:
        dir_path = os.path.join(dirpath, dirname)
        zip_file_list += glob.glob(os.path.join(dir_path, "*.zip"))
        rar_file_list += glob.glob(os.path.join(dir_path, "*.rar"))
        z7_file_list += glob.glob(os.path.join(dir_path, "*.7z"))

print("%d .zip files found" %(len(zip_file_list)))
for i in tqdm(range(len(zip_file_list)), desc = "extracting .zip files"):
    if os.path.exists(zip_file_list[i] + "_extract"):
        print("%s already extracted" %(zip_file_list[i]))
    else:
        print(zip_file_list[i])
        un_zip(zip_file_list[i])
    os.system(r"clear")

print("%d .rar files found" %(len(rar_file_list)))
for i in tqdm(range(len(rar_file_list)), desc = "extracting .rar files"):
    if os.path.exists(rar_file_list[i] + "_extract"):
        print("%s already extracted" %(rar_file_list[i]))
    else:
        print(rar_file_list[i])
        un_rar(rar_file_list[i])
    os.system(r"clear")

print("%d .7z files found" %(len(z7_file_list)))
for i in tqdm(range(len(z7_file_list)), desc = "extracting .7z files"):
    if os.path.exists(z7_file_list[i] + "_extract"):
        print("%s already extracted" %(z7_file_list[i]))
    else:
        print(z7_file_list[i])
        un_rar(z7_file_list[i])
    os.system(r"clear")

# np.savetxt("err_list.txt", np.array(err_file_list))
with open("err_list.txt", "w") as f:
    strs = '\n'
    f.write(strs.join(err_file_list))
