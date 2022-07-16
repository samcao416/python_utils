import sys
import numpy as np
import bpy


#fbx_dir = "/media/stereye/新加卷/Sam/car_models/64_porsche/Car Porsche 911 Carrera Cabriolet 2019.rar_extract/Porsche 911 Carrera Cabriolet 2019/Porsche 911 carrera Cabriolet.FBX"
fbx_dir = sys.argv[-2]
index = int(sys.argv[-1])
print("------------")
print("No.%04d: %s" %(index, fbx_dir))

def reset_blender():
    bpy.ops.object.select_all(action = 'DESELECT')
    for obj in bpy.data.objects:
        # print(ob.name)
        if obj.name == 'Camera':
            pass
        obj.select_set(True)
        bpy.ops.object.delete()

def import_fbx(path):
    
    bpy.ops.import_scene.fbx(filepath = path)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    return True

reset_blender()
import_fbx(fbx_dir)

bpy.ops.object.camera_add(align = 'VIEW', location = (0, 0, 10), rotation = (0, 0, -1), scale = (1, 1, 1))
#camera_obj = bpy.data.objects.new('Camera', align = 'VIEW', location = (-0.5851664543151855, -7.603287696838379, 1.8090481758117676), rotation = (1.24895, 0.0139616, 0.468225), scale = (1, 1, 1))
cam = bpy.data.objects['Camera']


#cam_data = bpy.data.cameras.new('camera')
#cam = bpy.data.objects.new('camera', cam_data)
#cam.location = (-0.5851664543151855, -7.603287696838379, 1.8090481758117676)
#bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

bpy.data.scenes['Scene'].render.image_settings.file_format = 'PNG'
bpy.data.scenes['Scene'].render.filepath = "./tests/test%04d.png" %(index)
bpy.data.scenes['Scene'].render.film_transparent = True
bpy.ops.render.render( write_still = True )

print("No.%04d finished." %(index))
print("------------")