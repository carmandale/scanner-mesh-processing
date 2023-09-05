import argparse
import bpy
import os
import math
from mathutils import Vector

print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ AddRig.v03 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ COMMAND LINE ARGUMENTS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default = "/Users/administrator/groove-test/takes/") 
    parser.add_argument('-s', '--software', help="software", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/")
    parser.add_argument('-cs', '--clean_start', help="to start with a clean scene", default=1)
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


def print_decorated(message, symbol="▬", padding=0):
    border = symbol * (len(message) + padding)
    decorated_message = f"\n{message}\n{border}"
    print(decorated_message)


def print_enhanced(text, text_color="white", label="", label_color="white", prefix="", suffix=""):
    color_code = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    if label == "":
        return print(f"{prefix}{color_code[text_color]}{text}{color_code['reset']}{suffix}")
    
    print(f"{prefix}[{color_code[label_color]}{label}{color_code['reset']}] {color_code[text_color]}{text}{color_code['reset']}{suffix}")


def pack_textures():
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            image.pack()


def find_middle_location(locations):
    if not locations:
        print_enhanced("find_middle_location failed | locations = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"find_middle_location | locations: {locations}", label="INFO", label_color="yellow")

    # Calculate the sum of all locations
    total_loc = Vector((0.0, 0.0, 0.0))
    for location in locations:
        total_loc += Vector(location)
    
    # Calculate the middle location by dividing the sum by the number of locations
    middle_loc = total_loc / len(locations)

    print_enhanced(f"{middle_loc}", label="MIDDLE LOCATION", label_color="green")
    
    return middle_loc


def minDis(x,y,z,verts):
    """
    Find the index of the vertex closest to the given coordinates.

    Args:
        x (float): x coordinate
        y (float): y coordinate
        z (float): z coordinate
        verts (list of Vector): list of vertex coordinates

    Returns:
        int: index of the vertex closest to the given coordinates
    """
    min_dist = 1e10
    min_idx = 0
    for idx, vert in enumerate(verts):
        x1, y1, z1 = tuple(vert)
        if abs(x1 - x) > 0.01:
            continue
        if abs(z1 - z) > 0.01:
            continue
        dist = math.sqrt((x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2)
        if dist < min_dist:
            min_dist = dist
            min_idx = idx
    return min_idx


def snapSkeleton(filepath, empties, verts):
    bpy.ops.wm.append(
    filepath=filepath,
    directory=os.path.join(os.path.join(filepath,"Armature/")), filename="Armature")
    bvh = bpy.context.selected_objects[0]
#   bvh.rotation_euler[0] = 1.5708
    bvh.location=[0,0,0]
#   bpy.ops.import_anim.bvh(filepath='Documents/Groove Jones/Blender Scripts/ref.bvh')
#   bvh = bpy.context.selected_objects[0]
    bvh.select_set(True)
    bpy.context.view_layer.objects.active = bvh
    bpy.ops.object.mode_set(mode='EDIT')
    bones_b = bvh.data.edit_bones
    bones_pos = {}
    for bone in bones_b:
        try:
            parent_loc = empties[translate[bone.name][0]]
            child_empty = translate[bone.name][1]
            if not child_empty==None:
                roll = bone.roll
                child_loc = empties[child_empty]
                bone.head = parent_loc
                bone.tail = child_loc  
                bone.roll = roll
                bones_pos[bone.name] =  [bone.head, bone.tail]   

            else:
                x_dist = bone.head[0] - parent_loc[0]
                y_dist = bone.head[1] - parent_loc[1]
                z_dist = bone.head[2] - parent_loc[2]
                
                bone.head = parent_loc
                bone.tail = (bone.tail[0] - x_dist, bone.tail[1] - y_dist,
                                bone.tail[2] - z_dist)
                bones_pos[bone.name] =  [bone.head, bone.tail]
        except Exception as e:
            print(e)
    # calculate the spine length
    x,y,z = bones_pos['mixamorig:Hips'][1]
    x1 = bones_pos['mixamorig:Hips'][1][0]
    y1 = bones_pos['mixamorig:Hips'][1][1]
    z1 = empties['shoulder_centre'][2]

    spine_length = math.sqrt((x-x1)**2 + (y-y1)**2 + (z-z1)**2)
    spine_bones_length = spine_length/3

    print("Spine length: {}".format(spine_length))
    print("Spine bones length: {}".format(spine_bones_length))

    Spine = bvh.data.edit_bones['mixamorig:Spine']
    roll = Spine.roll
    
    Spine.head = bones_pos['mixamorig:Hips'][1]
    Spine.tail[0] = bones_pos['mixamorig:Hips'][1][0]
    Spine.tail[1] = bones_pos['mixamorig:Hips'][1][1]
    Spine.tail[2] = bones_pos['mixamorig:Hips'][1][2] + spine_bones_length
    Spine.roll = roll

    Spine1 = bvh.data.edit_bones['mixamorig:Spine1']
    roll = Spine1.roll
    Spine1.head = Spine.tail
    Spine1.tail = (Spine.tail[0],Spine.tail[1],Spine.tail[2] + spine_bones_length)
    Spine1.roll = roll

    Spine2 = bvh.data.edit_bones['mixamorig:Spine2']
    roll = Spine2.roll 
    Spine2.head = Spine1.tail
    Spine2.tail = (Spine1.tail[0],Spine1.tail[1],Spine1.tail[2] + spine_bones_length)
    Spine2.roll = roll

    for bone in bones_b:
        if('Shoulder' in bone.name):
            roll = bone.roll
            bone.head[2] = empties['shoulder_centre'][2]
            bone.head[1] = Spine2.tail[1]
            bone.roll = roll
            
        elif(bone.name == 'mixamorig:Head'):
            y_list=[]
            for i in verts:
                if i[2] > empties['mouth_centre'][2]:
                    y_list.append(i[1])
            y_pos = sum(y_list)/len(y_list)

            length = bone.length
            roll = bone.roll
            bone.head = (empties['mouth_shoulder_centre'][0],y_pos,empties['mouth_centre'][2])
            bone.length = length
            bone.tail = (bone.head[0],bone.head[1],bone.head[2]+length)
            bone.roll = roll

        elif(bone.name == 'mixamorig:Neck'):
            roll = bone.roll
            bone.head = (empties['mouth_shoulder_centre'][0], Spine2.tail[1], empties['mouth_shoulder_centre'][2])
            bone.tail = (empties['mouth_shoulder_centre'][0],Spine2.tail[1], empties['mouth_centre'][2])
            bone.roll = roll
        elif(bone.name == 'mixamorig:Jaw'):
            roll = bone.roll
            bone.tail = (empties['mouth_centre'][0],bone.tail[1], empties['mouth_centre'][2])
            bone.roll = roll
        elif(bone.name == 'mixamorig:Jaw.001'):
            roll = bone.roll
            bone.tail = (empties['mouth_centre'][0],bone.tail[1]-.08, empties['mouth_centre'][2])
            bone.roll = roll
        elif(bone.name == 'mixamorig:RightHand'):
            roll = bone.roll
            bone.tail = empties['right_pinky']
            bone.roll = math.radians(7) # roll
        elif(bone.name == 'mixamorig:LeftHand'):
            roll = bone.roll
            bone.tail = empties['left_pinky']
            bone.roll = math.radians(-35) # roll
            
    # Fix the alignment of foot and toe
    for foot in ['Left','Right']:
        foot_bone = bvh.data.edit_bones['mixamorig:'+foot+'Foot']
        foot_to_toe_bone = bvh.data.edit_bones['mixamorig:'+foot+'ToeBase']
        roll1 = foot_bone.roll
        roll2 = foot_to_toe_bone.roll

        z_list = []
        for i in verts:
            if i[2] < empties[foot.lower()+'_heel'][2]:
                if i[1]<empties[foot.lower()+'_foot_index'][1]:
                    z_list.append(i[2])

        if len(z_list) > 0:
            z = sum(z_list) / len(z_list)
        else:
            z = 0  # or any default value you prefer

        foot_to_toe_bone.head[2] = z
        foot_to_toe_bone.tail[2] = z
        foot_bone.tail[2]=z

        x1 = foot_bone.head[0]
        y1 = foot_bone.head[1]
        x2 = foot_to_toe_bone.tail[0]
        y2 = foot_to_toe_bone.tail[1]
        
        y = foot_to_toe_bone.head[1]
        x = ((y-y1)/(y2-y1))*(x2-x1) + x1
        foot_bone.tail[0] = x
        foot_to_toe_bone.head[0] = x
        foot_bone.roll = roll1
        foot_to_toe_bone.roll = roll2

    #fix arm bone roll
    bvh.select_set(False)
    for bone in bvh.data.edit_bones:
        if "Arm" in bone.name or "ForeArm" in bone.name: # or "Hand"in bone.name:
            bone.select = True

    bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Z') 
    bpy.ops.object.editmode_toggle()


def createEmpties(_file, centre_joints, filter_joints, verts):

    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0,0,0), scale=(1,1,1))
    empty = bpy.context.active_object
    empty.name = 'root'

    keypoints = []
    with open(_file, 'r') as f:
        for keypoint in f.readlines():
            keypoints.append(keypoint)
            
    for centre_joint in centre_joints:
        _centre_loc = [i for i,s, in enumerate(keypoints) if centre_joint in s]
        _centre = [sum(list(map(float,x)))/2 for x in zip(keypoints[_centre_loc[0]].split(' ')[1:],keypoints[_centre_loc[1]].split(' ')[1:])]

        keypoints.append(f"{centre_joint}_CENTRE {' '.join(map(str,_centre))}")

    mouth_centre = [i for i,s, in enumerate(keypoints) if 'MOUTH_CENTRE' in s] 
    shoulder_centre =  [i for i,s, in enumerate(keypoints) if 'SHOULDER_CENTRE' in s]

    mouth_shoulder_centre = [sum(list(map(float,x)))/2 for x in zip(keypoints[mouth_centre[0]].split(' ')[1:],keypoints[shoulder_centre[0]].split(' ')[1:])]
    keypoints.append(f"MOUTH_SHOULDER_CENTRE {' '.join(map(str,mouth_shoulder_centre))}")

    nose = [i for i,s, in enumerate(keypoints) if 'NOSE' in s]

    nose_shoulder_centre = [sum(list(map(float,x)))/2 for x in zip(keypoints[nose[0]].split(' ')[1:],keypoints[shoulder_centre[0]].split(' ')[1:])]
    keypoints.append(f"NOSE_SHOULDER_CENTRE {' '.join(map(str,nose_shoulder_centre))}")
    empties = {}
    for keypoint in keypoints:
        if len([i for i,s in enumerate(filter_joints) if s in keypoint])>0:
            continue

        x = float(keypoint.split(' ')[1])
        z = float(keypoint.split(' ')[2])

        if('left_foot_index'==keypoint.split(' ')[0].lower()
            or 'right_foot_index'==keypoint.split(' ')[0].lower()):
            print('yes')
            z_list=[]
            foot = keypoint.split(' ')[0].lower().split('_')[0]
            for i in verts:
                if i[2] < empties[foot.lower()+'_ankle'][2]:
                    z_list.append(i[2])

            z = min(z_list)
            #z = sum(z_list)/len(z_list)

        y1 = 1
        y2 = -1

        min_idx1 = minDis(x,y1,z,verts)
        min_idx2 = minDis(x,y2,z,verts)

        y = (verts[min_idx1][1] + verts[min_idx2][1])/2

        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD',
        location=(x,y,z), scale=(1,1,1))
        empty_n = bpy.context.active_object
        empty_n.name = keypoint.split(' ')[0].lower()
        empties[empty_n.name] = (x,y,z)
        empty_n.parent = empty
        empty_n.empty_display_size = 0.1

    return empties


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

translate = {'mixamorig:LeftUpLeg': ['left_hip','left_knee'],
            'mixamorig:RightUpLeg': ['right_hip','right_knee'],
            'mixamorig:LeftLeg': ['left_knee', 'left_ankle'],
            'mixamorig:RightLeg': ['right_knee', 'right_ankle'],
            'mixamorig:LeftFoot': ['left_ankle','left_foot_index'],
            'mixamorig:RightFoot': ['right_ankle','right_foot_index'],
            'mixamorig:LeftToeBase':['left_foot_index', None],
            'mixamorig:RightToeBase':['right_foot_index', None],
            
            'mixamorig:LeftArm': ['left_shoulder','left_elbow'],
            'mixamorig:LeftForeArm': ['left_elbow','left_wrist'],
            'mixamorig:LeftHand': ['left_wrist', None],
            'mixamorig:RightArm': ['right_shoulder','right_elbow'],
            'mixamorig:RightForeArm': ['right_elbow','right_wrist'],
            'mixamorig:RightHand': ['right_wrist', None],
            #'mixamorig:Neck': ['mouth_shoulder_centre', 'mouth_centre'],
            'mixamorig:Hips' : ['hip_centre', None],
            'mixamorig:Spine2' : [None, 'shoulder_centre']
            }

def main():
    args = get_args()
    scan = str(args.scan)
    path = str(args.path)
    software_path = str(args.software)
    use_clean_start = int(args.clean_start)

    print_enhanced(path, label="PATH", label_color="cyan", prefix="\n")
    print_enhanced(scan, label="SCAN", label_color="cyan")
    print_enhanced(software_path, label="SOFTWARE", label_color="cyan")

    # Path to the folder where the keypoints file is stored
    keypoints_file_directory = os.path.join(path ,str(scan),"photogrammetry")
    # Name of the keypoints file
    keypoints_filename = str(scan) + '_results.txt'
    # Complete path
    keypoints_filepath = os.path.join(keypoints_file_directory, keypoints_filename)

    # Path to the folder where the obj file is stored
    obj_file_path = os.path.join(path ,str(scan),"photogrammetry")

    # Name of the obj file
    obj_file_name = str(scan) + '.blend' # changed to .blend from obj

    # Blend file with reference skeleton
    blend_file_path = software_path
    blend_file_name = "skeleton_template_v03.blend"
    blend_file = os.path.join(blend_file_path, blend_file_name)

    if use_clean_start == 1:
        print_decorated("Starting MAIN with a clean scene")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        print_enhanced("Creating World: START", label="INFO", label_color="yellow")
        bpy.ops.world.new()
        
        if not bpy.data.worlds:
            print_enhanced("World not found", label="ERROR", label_color="red")
            raise Exception
        
        bpy.context.scene.world = bpy.data.worlds[0]
        print_enhanced("Creating World: SUCCESS", label="INFO", label_color="yellow")

    # bpy.ops.import_scene.obj(filepath=os.path.join(obj_file_path,obj_file_name))
    bpy.ops.wm.append(
    filepath=os.path.join(obj_file_path, obj_file_name),
    directory=os.path.join(os.path.join(obj_file_path, obj_file_name,"Collection/")), filename="geo")
    obj = bpy.context.selected_objects[0]
    vertices = obj.data.vertices
    verts = [obj.matrix_world @ vert.co for vert in vertices]

    filter_joints = ['EYE','EAR']
    centre_joints = ['MOUTH', 'HIP', 'SHOULDER']
    empties = createEmpties(keypoints_filepath, centre_joints, filter_joints, verts)

    snapSkeleton(os.path.join(blend_file_path,blend_file),empties, verts)

    # rig the mesh
    bpy.ops.object.select_all(action='DESELECT')

    bpy.data.objects["Armature"].select_set(True)
    bpy.context.object.show_in_front = True
    bpy.data.objects["g0"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects['Armature']

    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="rig")

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects['g0']
    bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
    bpy.context.object.modifiers["CorrectiveSmooth"].iterations = 100

    #pack the textures
    pack_textures()
    # save the file for runShot script
    savepath = os.path.join(path ,str(scan),"photogrammetry",str(scan) + '-rig.blend')
    bpy.ops.wm.save_as_mainfile(filepath=savepath)

if __name__ == '__main__':
    main()