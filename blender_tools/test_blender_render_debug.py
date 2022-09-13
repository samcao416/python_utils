import sys
import os
import numpy as np
import bpy
import json
import math

#fbx_dir = "/media/stereye/新加卷/Sam/car_models/64_porsche/Car Porsche 911 Carrera Cabriolet 2019.rar_extract/Porsche 911 Carrera Cabriolet 2019/Porsche 911 carrera Cabriolet.FBX"


def reset_blender():
    '''
    This function is used to delete all the context in blender.
    It will NOT remove the default Light in the scene.
    '''
    bpy.ops.object.select_all(action = 'DESELECT')
    for obj in bpy.data.objects:
        # print(ob.name)
        if obj.name == ('Light' or 'Camera'):
            continue
        obj.select_set(True)
        bpy.ops.object.delete()

def import_fbx(path):
    
    bpy.ops.import_scene.fbx(filepath = path)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    return True

def rotateY(a,point):
    # a for rotation angle
    rotate_M = np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    return rotate_M @ point

def rotateX(a,point):
    rotate_M = np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
    return rotate_M @ point

def dealRotate(bd_min,bd_max,loc,axis):
    for obj in bpy.data.objects:
        if ('Light' in obj.name) or ('Camera' in obj.name):
            continue
        if obj.parent is None:
            obj.rotation_euler.rotate_axis(axis, math.radians(90))
    # bpy.ops.transform.rotate(value=math.pi/2, orient_axis=axis, orient_matrix_type='VIEW')
    bd_max = bd_max - loc
    bd_min = bd_min - loc
    if axis == 'X':
        bd_min = rotateX(math.pi/2,bd_min)
        bd_max = rotateX(math.pi/2,bd_max)
    if axis == 'Y':
        bd_min = rotateY(math.pi/2,bd_min)
        bd_max = rotateY(math.pi/2,bd_max)
    

    bd = np.stack([bd_min,bd_max],axis=0)
    print(bd)
    bd_min = np.min(bd,axis = 0)+loc
    bd_max = np.max(bd,axis = 0)+loc

    translate_bd(bd_min,bd_max)

    zmax = bd_max[2]
    xyz_min = (bd_min - bd_max) / 2
    xyz_max = (bd_max - bd_min) / 2
    bd_min[2] = 0
    bd_max[2] = zmax
    return bd_min, bd_max

def cal_bd():
    bound_list = []
    for obj in bpy.data.objects:
        #print(obj.name)
        matirx_world = np.array(obj.matrix_world)

        if not (('light' in obj.name) | ('Light' in obj.name) | ('Camera' in obj.name) | ('camera' in obj.name)):
            for bound_point in obj.bound_box:
                bound_point = matirx_world[:3, :3] @ np.array(bound_point) + matirx_world[:3,3]
                bound_list.append(bound_point)
    
    bd_array = np.array(bound_list)

    bd_min = np.min(bd_array, axis = 0)
    bd_max = np.max(bd_array, axis = 0)

    hwd = bd_max - bd_min

    min_index = np.argmin(hwd, axis = 0)
    max_index = np.argmax(hwd, axis = 0)

    return bd_min, bd_max, hwd, min_index, max_index

def get_scale_co(hwd):
    h = np.max(hwd)
    scale = 1
    if 0.1 < h < 1.0:
        scale = 10
    elif 0.01 < h < 0.1:
        scale = 100
    elif 100 > h >= 10:
        scale = 0.1
    elif 1000 > h >= 100:
        scale = 0.01
    elif h >= 1000:
        scale = 0.001
    return scale

def scale(hwd):

    scale = get_scale_co(hwd)
    selectCar()
    bpy.ops.transform.resize(value = (scale, scale, scale), orient_type = 'VIEW', orient_matrix = ((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type = 'GLOBAL', mirror = False, use_proportional_edit = False, proportional_edit_falloff = 'SMOOTH', proportional_size = 1, use_proportional_connected = False, use_proportional_projected = False)

def translate_bd(bd_min,bd_max):
    hwd = bd_max-bd_min
    h = np.max(hwd)
    scale = 1
    translatez =  bd_min[2]/1000
    translatey = ((bd_max[1]+bd_min[1])/2)
    translatex = ((bd_max[0]+bd_min[0])/2)
    selectCar()
    bpy.ops.transform.translate(value=(-translatex, -translatey, -translatez), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.select_all(action='DESELECT')

def selectCar():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="Light", case_sensitive=False, extend=True)
    bpy.ops.object.select_pattern(pattern="Camera", case_sensitive=False, extend=True)
    bpy.ops.object.select_pattern(pattern="Light", case_sensitive=False, extend=True)
    bpy.ops.object.select_pattern(pattern="Camera", case_sensitive=False, extend=True)
    bpy.ops.object.select_all(action='INVERT')

def cal_cam_loc(hwd):
    scale = 1
    scale = get_scale_co(hwd)
    hwd = hwd * scale
    len = np.max(hwd*1.5) # TODO: the coefficient should be modified
    z = np.min(hwd*1.5)
    return len,z

def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list

def parent_obj_to_camera(b_camera):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.collection.objects.link(b_empty)
    bpy.context.view_layer.objects.active = b_empty
    # scn.objects.active = b_empty
    return b_empty

if __name__ == "__main__":

    '''
            Initialization       
    '''
    DEBUG = True
    if DEBUG:
        fbx_dir = "/media/stereye/新加卷/Sam/car_models/130_benz/Mercedes-Benz C63 AMG Coupe 2017.zip_extract/Mercedes-Benz_C63_AMG_Coupe_2017/Mercedes-Benz_C63_AMG_Coupe_2017_set.fbx"
        # fbx_dir = "/media/stereye/新加卷/Sam/car_models/77_chevrolet/Chevrolet Camaro SS 2020 3D model.zip_extract/Chevrolet Camaro SS 2020 3D model/Chevrolet Camaro/camaro.fbx"
        #fbx_dir = "/media/stereye/新加卷/Sam/car_models/64_porsche/porsche-cayenne-gts-coupe-2020.zip_extract/porsche-cayenne-gts-coupe-2020/porsche-cayenne-gts-coupe-2020.fbx" # for bottom up debug
        index = 0
        output_dir = "./outputs_debug/No_%04d" %(index)
    else:
        fbx_dir = sys.argv[-2]
        index = int(sys.argv[-1])
        output_dir = "./outputs/No_%04d" %(index)
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    # if not os.path.isdir(os.path.join(output_dir, "images")):
    #     os.makedirs(os.path.join(output_dir, "images"))

    VIEWS = 5
    RESOLUTION = 800
    DEPTH_SCALE = 1.4
    COLOR_DEPTH = 8
    FORMAT = 'PNG'
    UPPER_VIEWS = True
    CIRCLE_FIXED_START = (0,0,0)
    CIRCLE_FIXED_END = (.7,0,0)
    branches = ['z_up', 'z_down']
    print("------------")
    print("No.%04d: %s" %(index, fbx_dir))

    '''
            Reset blender and import model    
    '''
    reset_blender()
    import_fbx(fbx_dir)

    scene = bpy.context.scene
    ### Wenchao Part Start
    ### dealing with models in the scene
    bound_list = []
    for obj in bpy.data.objects:
        if not (('light' in obj.name) & ('Light' in obj.name) & ('Camera' in obj.name) & ('camera' in obj.name)):
            for bound_point in obj.bound_box:
                bound_list.append(np.array(bound_point))
                
    loc = np.array(bpy.data.objects[1].location)


    bd_min, bd_max, hwd, min_index, max_index = cal_bd()
    # light camera select



    cam_len,cam_z = cal_cam_loc(hwd)

    if (max_index == 0) | (max_index == 1):
        translate_bd(bd_min,bd_max)

    if max_index == 2 :
        selectCar()
        if min_index == 1:
            min_box, max_box = dealRotate(bd_min,bd_max,loc,axis='X')
        if min_index == 0:
            min_box, max_box = dealRotate(bd_min,bd_max,loc,axis='Y')
        scale_co = get_scale_co(hwd)
        bd_min = (min_box - loc) / scale_co + loc
        bd_max = (max_box - loc) / scale_co + loc

    scale(hwd)

    if max_index != 2:
        bd_min, bd_max, hwd, min_index, max_index = cal_bd()
    
    bb_matrix = []
    bb_matrix.append(list(bd_max))
    bb_matrix.append(list(bd_min))

    z_mean = (bb_matrix[0][2] + bb_matrix[1][2]) / 2

    # Render Optimizations
    scene.render.use_persistent_data = True

    # Set up rendering of depth map.
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links

    for layer in scene.view_layers:
        layer.name = "RenderLayer"

    # Add passes for additionally dumping albedo and normals.
    scene.view_layers["RenderLayer"].use_pass_normal = True
    scene.render.image_settings.file_format = str(FORMAT)
    scene.render.image_settings.color_depth = str(COLOR_DEPTH)

    if 'Custom Outputs' not in tree.nodes:
        # Create input render layer node.
        render_layers = tree.nodes.new('CompositorNodeRLayers')
        render_layers.label = 'Custom Outputs'
        render_layers.name = 'Custom Outputs'

        depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
        depth_file_output.label = 'Depth Output'
        depth_file_output.name = 'Depth Output'
        if FORMAT == 'OPEN_EXR':
            links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
        else:
        # Remap as other types can not represent the full range of depth.
            map = tree.nodes.new(type="CompositorNodeMapRange")
            # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
            map.inputs['From Min'].default_value = 0
            map.inputs['From Max'].default_value = 8
            map.inputs['To Min'].default_value = 1
            map.inputs['To Max'].default_value = 0
            links.new(render_layers.outputs['Depth'], map.inputs[0])

            links.new(map.outputs[0], depth_file_output.inputs[0])

        normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
        normal_file_output.label = 'Normal Output'
        normal_file_output.name = 'Normal Output'
        links.new(render_layers.outputs['Normal'], normal_file_output.inputs[0])

    # Background
    scene.render.dither_intensity = 0.0
    scene.render.film_transparent = True

    # Create collection for objects not to render with background

        
    objs = [ob for ob in scene.objects if ob.type in ('EMPTY') and 'Empty' in ob.name]
    bpy.ops.object.delete({"selected_objects": objs})
    scene.render.resolution_x = RESOLUTION
    scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100

    ### Wenchao part ends


    # Add a camera
    bpy.ops.object.camera_add(align = 'VIEW', location = (0, 0, 0), rotation = (0, 0, -1), scale = (1, 1, 1))
    #camera_obj = bpy.data.objects.new('Camera', align = 'VIEW', location = (-0.5851664543151855, -7.603287696838379, 1.8090481758117676), rotation = (1.24895, 0.0139616, 0.468225), scale = (1, 1, 1))
    cam = bpy.data.objects['Camera']
    scene.camera = cam

    ## Wenchao part starts
    for j in range(2):
        branch_dir = os.path.join(output_dir, branches[j])
        if not os.path.isdir(branch_dir):
            os.makedirs(branch_dir)

        contents = ['rgb', 'depth', 'normal']
        for content in contents:
            if not os.path.isdir(os.path.join(branch_dir, content)):
                os.makedirs(os.path.join(branch_dir, content))

        if j:
            cam_z = 2 * z_mean - cam_z
        cam.location = (0, cam_len, cam_z)
        cam_constraint = cam.constraints.new(type='TRACK_TO')
        cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        cam_constraint.up_axis = 'UP_Y'
        b_empty = parent_obj_to_camera(cam)
        cam_constraint.target = b_empty

        # Data to store in JSON file
        out_data = {
            'camera_angle_x': bpy.data.objects['Camera'].data.angle_x,
            'bound_box': bb_matrix,
            'fbx_path' : fbx_dir,
        }

        from math import radians

        stepsize = 360.0 / VIEWS
        vertical_diff = CIRCLE_FIXED_END[0] - CIRCLE_FIXED_START[0]
        rotation_mode = 'XYZ'


        for output_node in [tree.nodes['Depth Output'], tree.nodes['Normal Output']]:
            output_node.base_path = ''

        out_data['frames'] = []

        ### Wenchao part ends

        bpy.data.scenes['Scene'].render.image_settings.file_format = 'PNG'
        
        bpy.data.scenes['Scene'].render.film_transparent = True
        
        ### Wenchao part starts
        b_empty.rotation_euler = CIRCLE_FIXED_START
        b_empty.rotation_euler[0] = CIRCLE_FIXED_START[0] + vertical_diff

        for i in range(0, VIEWS):
            # if DEBUG:
            #     i = np.random.randint(0,VIEWS)
            #     b_empty.rotation_euler[0] = CIRCLE_FIXED_START[0] + (np.cos(radians(stepsize*i))+1)/2 * vertical_diff
            #     b_empty.rotation_euler[2] += radians(2*stepsize*i)
        
            print("Rotation {}, {}".format((stepsize * i), radians(stepsize * i)))
            bpy.data.scenes['Scene'].render.filepath = os.path.join(branch_dir,"rgb", "%04d.png" %(i))

            tree.nodes['Depth Output'].file_slots[0].path = os.path.join(branch_dir,"depth", "%04d" %(i))
            tree.nodes['Normal Output'].file_slots[0].path = os.path.join(branch_dir,"normal", "%04d" %(i))


            bpy.ops.render.render(write_still=True)  # render still

            frame_data = {
                'file_path': os.path.join('rgb' + os.path.basename(scene.render.filepath)),
                # 'cam_location': list(cam.location),
                'rotation': radians(stepsize),
                'transform_matrix': listify_matrix(cam.matrix_world)
            }
            out_data['frames'].append(frame_data)

            b_empty.rotation_euler[0] = CIRCLE_FIXED_START[0] + (np.cos(radians(stepsize*i))+1)/2 * vertical_diff
            b_empty.rotation_euler[2] += radians(2*stepsize)


        with open(branch_dir + '/' + 'transforms.json', 'w') as out_file:
            json.dump(out_data, out_file, indent=4)

    # Wenchao part ends
    
    #bpy.ops.render.render( write_still = True )

    print("No.%04d finished." %(index))
    print("------------")
