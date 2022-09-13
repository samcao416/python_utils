from ast import Raise
from pickle import FALSE
import numpy as np
import os
import bpy
import json
import math
import sys
from math import radians
import mathutils
import random

def reset_blender():
    '''
    This function is used to delete all the context in blender.
    It will NOT remove the default Light in the scene.
    '''
    bpy.ops.object.select_all(action = 'DESELECT')
    for obj in bpy.data.objects:
        # print(ob.name)
        if obj.name == ('Camera') or obj.name == ('Light'):
            continue
        obj.select_set(True)
        bpy.ops.object.delete()
    # bpy.ops.object.light_add(type = 'POINT', radius = 1, align = 'WORLD', location = (10, 10, 10), scale = (1,1, 1))
    bpy.data.lights['Light'].energy = 10000

def import_fbx(path):
    
    bpy.ops.import_scene.fbx(filepath = path)
    bpy.ops.object.select_all(action = 'DESELECT')
    
    return True

def rotateY(a,point):
    # rotation matrix for a point along Y axis
    rotate_M = np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    return rotate_M @ point

def rotateX(a,point):
    # rotation matrix for a point along X axis
    rotate_M = np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
    return rotate_M @ point

def dealRotate(bd_min,bd_max,loc,axis):
    '''
    This function first rotate all the car long a certain axis for 90 degrees
    Then rotate the bounding box along a certrain axis for 90 degrees

    '''

    # rotation all the objects in the scene other than Light and Camera
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
    bd_min = np.min(bd,axis = 0)+loc
    bd_max = np.max(bd,axis = 0)+loc

    translate_bd(bd_min,bd_max)

    zmax = bd_max[2] - bd_min[2]
    xyz_min = (bd_min - bd_max) / 2
    xyz_max = (bd_max - bd_min) / 2
    bd_min = xyz_min
    bd_max = xyz_max
    bd_min[2] = 0
    bd_max[2] = zmax
    return bd_min, bd_max

def cal_bd():
    '''
    This function calculate the six coordinate of the bounding box (bd_max, bd_min)
    hwd: the three length(dimension) of the bounding box
    max_index : the longest side index of the bounding box
    min_index : the shortest side index of the bounding box
    '''
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
    translatez =  bd_min[2]
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

def draw_bbox(bbox):
    bbox = np.array(bbox)
    if bbox.shape != (2, 3):
        raise TypeError("Wrong Dimenstion of Bbox")
    # cal culation the middle and dimension of the bbox
    bbox_center = np.mean(bbox, axis = 0)
    bbox_dimension = bbox[0] - bbox[1]

    bpy.ops.mesh.primitive_cube_add(location = (bbox_center[0], bbox_center[1], bbox_center[2]), \
                                    scale = (bbox_dimension[0] /2, bbox_dimension[1]/2, bbox_dimension[2]/2))
    bpy.data.objects['Cube'].display_type = 'BOUNDS'

def delete_bbox():
    obj = bpy.data.objects['Cube']
    obj.select_set(True)
    bpy.ops.object.delete()


def add_disturbance(matrix):
    ""
    pass

def generate_cam_path_mat(keyword, bb_matrix, view_num = 50):
    cam_position = [0,0, bb_matrix[1][2] * 1.1]
    cam_pose = np.zeros([4,4])
    cam_pose[3,3] = 1
    if "back" in keyword:
        cam_pose[0][0] = -1.0
        cam_pose[1][2] =  1.0
        cam_pose[2][1] =  1.0
        y_start = bb_matrix[1][1] * 10
        y_end = bb_matrix[1][1] * 1.2
        
    elif "front" in keyword:
        cam_pose[0][0] =  1.0
        cam_pose[1][2] = -1.0
        cam_pose[2][1] =  1.0
        y_start = bb_matrix[0][1] * 10
        y_end = bb_matrix[0][1] * 1.2
    else:
        raise RuntimeError("You have to sepecify a certain looking direciton: front or back")

    y_step = (y_end - y_start) / (view_num -1)

    if "side" in keyword:
        cam_position[0] = bb_matrix[1][0] * 1.1
    else:
        pass
    
    mat_list = []
    cam_pose[0][3] = cam_position[0]
    cam_pose[2][3] = cam_position[2]

    for i in range(view_num):
        
        cam_pose[1][3] = y_start + y_step * i
        
        mat_list.append(mathutils.Matrix(cam_pose))

    return mat_list

if __name__ == "__main__":
    '''
        Initialization Arguments
    '''
    DEBUG = False
    SHOW_BBOX = True
    DISTURB = False
    VIEWS = 50
    RESOLUTION = 800
    DEPTH_SCALE = 1.4
    COLOR_DEPTH = 32
    FORMAT = 'OPEN_EXR'
    FOCAL = 15

    branches = ['z_up', 'z_x_180']
    cam_directions = ['0_front_mid','1_back_mid', '2_front_side', '3_back_side']
    #cam_directions = ['1_mid']
    if SHOW_BBOX:
        contents = ['rgb', 'depth', 'normal', 'bbox']
    else:
        contents = ['rgb', 'depth', 'normal']

    '''
        Step 1: import FBX and scene
    '''

    if DEBUG:
        # fbx_dir = "/media/stereye/新加卷/Sam/car_models/130_benz/Mercedes-Benz C63 AMG Coupe 2017.zip_extract/Mercedes-Benz_C63_AMG_Coupe_2017/Mercedes-Benz_C63_AMG_Coupe_2017_set.fbx"
        # fbx_dir = "/media/stereye/新加卷/Sam/car_models/77_chevrolet/Chevrolet Camaro SS 2020 3D model.zip_extract/Chevrolet Camaro SS 2020 3D model/Chevrolet Camaro/camaro.fbx"
        #fbx_dir = "/media/stereye/新加卷/Sam/car_models/64_porsche/porsche-cayenne-gts-coupe-2020.zip_extract/porsche-cayenne-gts-coupe-2020/porsche-cayenne-gts-coupe-2020.fbx" # for bottom up debug
        # fbx_dir = "/media/stereye/新加卷/Sam/car_models/130_benz/Mercedes-Benz 300 SL 1957.zip_extract/Mercedes-Benz 300 SL 1957/Mercedes-Benz 300 SL 1957 3D model/Mercedes-Benz_300_SL_(W198_II)_roadster_1957.fbx"
        # fbx_dir = "/media/stereye/新加卷/Sam/car_models/64_porsche/porsche-911-gt3-cup.zip_extract/porsche-911-gt3-cup/porsche-911-gt3-cup.fbx" 
        fbx_dir = "/media/stereye/新加卷/Sam/car_models/130_benz/Mercedes-Benz 300d (W189) 1957.zip_extract/Mercedes-Benz 300d (W189) 1957/Mercedes-Benz 300d (W189) 1957 3D model/Mercedes-Benz_300d_(W189)_1957.fbx"
        index = 0
        output_dir = "./outputs_no_bg_line_debug/No_%04d" %(index)
    else:
        fbx_dir = sys.argv[-2]
        index = int(sys.argv[-1])
        output_dir = "./outputs_no_bg_line/No_%04d" %(index)

    
    reset_blender()
    import_fbx(fbx_dir)
 
    '''
        Step 2: Make Dirs
    '''
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    for branch in branches:
        branch_dir = os.path.join(output_dir, branch)
        for cam_direction in cam_directions:
            cam_direction_dir = os.path.join(branch_dir, cam_direction)
            # if not os.path.isdir(cam_direction_dir):
            #     os.makedirs(cam_direction_dir)

        
            for content in contents:
                if not os.path.isdir(os.path.join(cam_direction_dir, content)):
                    os.makedirs(os.path.join(cam_direction_dir, content))
    print("------------")
    print("No.%04d: %s" %(index, fbx_dir))


    '''
        Step 3: Transforming
    '''
    scene = bpy.context.scene
    bound_list = []
    for obj in bpy.data.objects:
        if not (('light' in obj.name) & ('Light' in obj.name) & ('Camera' in obj.name) & ('camera' in obj.name)):
            for bound_point in obj.bound_box:
                bound_list.append(np.array(bound_point))
                
    loc = np.array(bpy.data.objects[3].location) 
    # all the objects of the model got the same location, subtract by this location will center the model


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
        bd_min = (min_box - loc) * scale_co + loc
        bd_max = (max_box - loc) * scale_co + loc

    scale(hwd)

    if max_index != 2:
        bd_min, bd_max, hwd, min_index, max_index = cal_bd()
    
    bb_matrix = []
    bb_matrix.append(list(bd_max))
    bb_matrix.append(list(bd_min))
    
    for layer in scene.view_layers:
        layer.name = "RenderLayer"


    # Add a camera
    # bpy.ops.object.camera_add(align = 'VIEW', location = (0, 0, 0), rotation = (0, 0, -1), scale = (1, 1, 1))
    #camera_obj = bpy.data.objects.new('Camera', align = 'VIEW', location = (-0.5851664543151855, -7.603287696838379, 1.8090481758117676), rotation = (1.24895, 0.0139616, 0.468225), scale = (1, 1, 1))
    
    rotate_or_not = True
    if rotate_or_not:
        selectCar()
        if (max_index != 2) or (min_index == 1):
            loc = np.array(bpy.data.objects[3].location)
            bd_min, bd_max = dealRotate(bd_min, bd_max, loc, axis = 'X')
            loc = np.array(bpy.data.objects[3].location)
            min_box, max_box = dealRotate(bd_min, bd_max, loc, axis = 'X')
        elif min_index == 0:
            loc = np.array(bpy.data.objects[3].location)
            bd_min, bd_max = dealRotate(bd_min, bd_max, loc, axis = "Y")
            loc = np.array(bpy.data.objects[3].location)
            min_box, max_box = dealRotate(bd_min, bd_max, loc, axis = "Y")
        bb_matrix = []
        bb_matrix.append(list(min_box))
        bb_matrix.append(list(max_box))

    '''
        Step 4: Rendering
    '''

    # Render Optimizations
    scene = bpy.context.scene
    scene.render.use_persistent_data = True
    
    
    cam = bpy.data.objects['Camera']
    scene.camera = cam

    # set focal
    bpy.data.cameras[0].lens = FOCAL# set focal length 

    for j in range(len(branches)):
        branch_dir = os.path.join(output_dir, branches[j])

        # cam.location = (0, cam_len, cam_z)
        # cam_constraint = cam.constraints.new(type='TRACK_TO')
        # cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        # cam_constraint.up_axis = 'UP_Y'
        
        if j != 0:
            selectCar()
            bb_matrix = []
            if (max_index != 2) or (min_index == 1):
                loc = np.array(bpy.data.objects[3].location)
                bd_min, bd_max = dealRotate(bd_min, bd_max, loc, axis = 'X')
                loc = np.array(bpy.data.objects[3].location)
                min_box, max_box = dealRotate(bd_min, bd_max, loc, axis = 'X')
            elif min_index == 0:
                loc = np.array(bpy.data.objects[3].location)
                bd_min, bd_max = dealRotate(bd_min, bd_max, loc, axis = "Y")
                loc = np.array(bpy.data.objects[3].location)
                min_box, max_box = dealRotate(bd_min, bd_max, loc, axis = "Y")
            bb_matrix.append(list(min_box))
            bb_matrix.append(list(max_box))
        

        # Set up rendering of depth map.
        scene.use_nodes = True
        tree = scene.node_tree
        links = tree.links
        
        # Add passes for additionally dumping albedo and normals.
        scene.view_layers["RenderLayer"].use_pass_normal = True
        scene.view_layers["RenderLayer"].use_pass_z = True
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

        for layer in scene.view_layers:
            layer.name = "RenderLayer"
        
        objs = [ob for ob in scene.objects if ob.type in ('EMPTY') and 'Empty' in ob.name]
        bpy.ops.object.delete({"selected_objects": objs})
        scene.render.resolution_x = RESOLUTION
        scene.render.resolution_y = RESOLUTION
        scene.render.resolution_percentage = 100

        
        out_data = {
                'camera_angle_x': bpy.data.objects['Camera'].data.angle_x,
                'focal': bpy.data.cameras[0].lens,
                'bound_box': bb_matrix,
                'fbx_path' : fbx_dir,
            }

        

        # stepsize = 360.0 / VIEWS
        # vertical_diff = CIRCLE_FIXED_END[0] - CIRCLE_FIXED_START[0]
        # rotation_mode = 'XYZ'


        for output_node in [tree.nodes['Depth Output'], tree.nodes['Normal Output']]:
            output_node.base_path = ''

        out_data['frames'] = []
        
        bpy.data.scenes['Scene'].render.image_settings.file_format = 'PNG'
        bpy.data.scenes['Scene'].render.image_settings.color_depth = '8'
        bpy.data.scenes['Scene'].render.film_transparent = True
        
        ### Wenchao part starts
        # b_empty = parent_obj_to_camera(cam)
        # cam_constraint.target = b_empty
        # b_empty.rotation_euler = CIRCLE_FIXED_START
        # b_empty.rotation_euler[0] = CIRCLE_FIXED_START[0] + vertical_diff

        # cam_start = bb_matrix[0][1] * 3
        # cam_step = -2 * cam_start / VIEWS
        for k in range(len(cam_directions)):
            
            # if k == 1:
            #     scene.camera.matrix_world = mathutils.Matrix([[0.0000, -0.8192, 0.5736, 0.0], #-cos sin
            #                                                   [1.0000,  0.0000, 0.0000, 0.0], 
            #                                                   [0.0000,  0.5736, 0.8192, 0.0], # sin cos
            #                                                   [0.0000,  0.0000, 0.0000, 1.0]])
            # elif k == 2:
            #     scene.camera.matrix_world = mathutils.Matrix([[-0.5035, -0.7077, 0.4956, 0.0],
            #                                                   [ 0.8640, -0.4125, 0.2888, 0.0],
            #                                                   [-0.0000,  0.5736, 0.8192, 0.0],
            #                                                   [ 0.0000,  0.0000, 0.0000, 1.0]])
            # elif k == 0:
            #     scene.camera.matrix_world = mathutils.Matrix([[ 0.5004, -0.7092,  0.4966, 0.0],
            #                                                   [ 0.8658,  0.4099, -0.2870, 0.0],
            #                                                   [-0.0000,  0.5736,  0.8192, 0.0],
            #                                                   [ 0.0000,  0.0000,  0.0000, 1.0]])

            # scene.camera.matrix_world[0][3] = bb_matrix[1][0] * 5
            # scene.camera.matrix_world[1][3] = cam_start
            # scene.camera.matrix_world[2][3] = bb_matrix[1][2] * 5
            mat_list = generate_cam_path_mat(keyword=cam_directions[k], bb_matrix=bb_matrix, view_num=VIEWS)

            # if DISTURB:
            #     scene.camera.matrix_world = add_disturbance(scene.camera.matrix_world)

            for i in range(0, VIEWS):
                
                #scene.camera.matrix_world[1][3] += cam_step
                #scene.camera.location.y += cam_step
                cam.matrix_world = mat_list[i]
                #print("Rotation {}, {}".format((stepsize * i), radians(stepsize * i)))
                bpy.data.scenes['Scene'].render.filepath = os.path.join(branch_dir, cam_directions[k], "rgb", "%04d.png" %(i))

                tree.nodes['Depth Output'].file_slots[0].path = os.path.join(branch_dir,cam_directions[k], "depth", "%04d" %(i))
                tree.nodes['Normal Output'].file_slots[0].path = os.path.join(branch_dir, cam_directions[k], "normal", "%04d" %(i))


                bpy.ops.render.render(write_still=True)  # render still

                if SHOW_BBOX:
                    draw_bbox(bb_matrix)
                    scene.view_layers["RenderLayer"].use_pass_normal = False
                    scene.view_layers["RenderLayer"].use_pass_z = False  

                    bpy.data.scenes['Scene'].render.filepath = os.path.join(branch_dir,cam_directions[k], "bbox", "%04d.png" %(i))
                    bpy.ops.render.render(write_still=True)

                    scene.view_layers["RenderLayer"].use_pass_normal = True
                    scene.view_layers["RenderLayer"].use_pass_z = True
                    delete_bbox()


                frame_data = {
                    'file_path': os.path.join('rgb' , os.path.basename(scene.render.filepath)),
                    # 'cam_location': list(cam.location),
                    'transform_matrix': listify_matrix(cam.matrix_world)
                }
                out_data['frames'].append(frame_data)

            # b_empty.rotation_euler[0] = CIRCLE_FIXED_START[0] + (np.cos(radians(stepsize*i))+1)/2 * vertical_diff
            # b_empty.rotation_euler[2] += radians(2*stepsize)
        
        
            
            
            with open(branch_dir + '/'+cam_directions[k] + '/' + 'transforms.json', 'w') as out_file:
                    json.dump(out_data, out_file, indent=4)

    print("No.%04d finished." %(index))
    print("------------")