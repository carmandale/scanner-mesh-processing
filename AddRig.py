import argparse
import bpy
import os
import math
from bpy import context
import pprint

print('_______________________________________')
print('_______________________________________')
print('________________ADD RIG________________')
print('________________3.30.23________________')
print('_______________________________________')

def get_args():
  parser = argparse.ArgumentParser()
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--scan', help="scan name")
  parser.add_argument('-m', '--path', help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") 
  parser.add_argument('-s', '--software', help="software", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/") 
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args
 
# Constants
FILTER_JOINTS = ['EYE', 'EAR']
CENTRE_JOINTS = ['MOUTH', 'HIP', 'SHOULDER']
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
            
def pack_textures():
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            image.pack()


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

def append_armature(filepath):
    """
    Appends the armature object from the specified filepath.
    """
    bpy.ops.wm.append(
        filepath=filepath,
        directory=os.path.join(os.path.join(filepath, "Armature/")),
        filename="Armature"
    )
    return bpy.context.selected_objects[0]

def get_bone_positions(armature_obj, empties):
    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bones_b = armature_obj.data.edit_bones
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

        # Set the position of Jaw
        if bone.name == 'mixamorig:Jaw':
                    roll = bone.roll
                    bone.tail = (empties['mouth_centre'][0],bone.tail[1],
                         empties['mouth_centre'][2])
                    bone.roll = roll
                    bones_pos[bone.name] = [bone.head, bone.tail]

        # Set the position of Jaw.001
        if bone.name == 'mixamorig:Jaw.001':
                    roll = bone.roll
                    bone.tail = (empties['mouth_centre'][0], bone.tail[1] - 0.08, 
                                 empties['mouth_centre'][2])
                    bone.roll = roll
                    bones_pos[bone.name] = [bone.head, bone.tail]

        # Set the position of LeftHand
        if bone.name == 'mixamorig:LeftHand':
                    roll = bone.roll
                    bone.tail = empties['left_pinky']
                    bone.roll = math.radians(-35)
                    bones_pos[bone.name] = [bone.head, bone.tail]

        # Set the position of RightHand
        if bone.name == 'mixamorig:RightHand':
                    roll = bone.roll
                    bone.tail = empties['right_pinky']
                    bone.roll = math.radians(7)
                    bones_pos[bone.name] = [bone.head, bone.tail]
                    

    bpy.ops.object.mode_set(mode='OBJECT')

    return bones_pos

def calculate_spine_length(armature, bones_pos, empties):
    """
    Calculate the spine length based on the positions of the hip bone and the shoulder center.

    Args:
        bones_pos: dictionary containing the positions of the bones
        empties: dictionary containing the positions of the empties

    Returns:
        spine_length: the calculated spine length
    """
    if armature.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    x, y, z = bones_pos['mixamorig:Hips'][1]
    x1, y1, z1 = empties['shoulder_centre']
    
    spine_length = math.sqrt((x - x1) ** 2 + (y - y1) ** 2 + (z - z1) ** 2)
    spine_bones_length = spine_length / 3

    print("Spine length: {}".format(spine_length))
    print("Spine bones length: {}".format(spine_bones_length))

    return spine_bones_length

def adjust_spine(armature, bones_pos, spine_bones_length):
    if armature.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    spine = armature.data.edit_bones["mixamorig:Spine"]
    spine1 = armature.data.edit_bones["mixamorig:Spine1"]
    spine2 = armature.data.edit_bones["mixamorig:Spine2"]
    roll = spine.roll

    spine.head = bones_pos['mixamorig:Hips'][1]
    spine.tail[0] = bones_pos['mixamorig:Hips'][1][0]
    spine.tail[1] = bones_pos['mixamorig:Hips'][1][1]
    spine.tail[2] = bones_pos['mixamorig:Hips'][1][2] + spine_bones_length
    spine.roll = roll
    
    
    roll = spine1.roll
    spine1.head = spine.tail
    spine1.tail = (spine.tail[0],spine.tail[1],spine.tail[2] + spine_bones_length)
    spine1.roll = roll
    
    
    roll = spine2.roll 
    spine2.head = spine1.tail
    spine2.tail = (spine1.tail[0],spine1.tail[1],spine1.tail[2] + spine_bones_length)
    spine2.roll = roll

    bpy.ops.object.mode_set(mode='OBJECT')

    return armature

def set_shoulder_positions(armature, empties):
    if armature.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bones = armature.data.edit_bones
    
    for bone_name in ['mixamorig:LeftShoulder', 'mixamorig:RightShoulder']:
        bone = bones.get(bone_name)
        if bone is None:
            print(bone_name, 'not found')
            continue
        
        try:
            bone.head = empties['shoulder_centre']
            bone.tail = empties[bone_name.lower()]
        except KeyError:
            print(bone_name.lower(), 'not found - I am in the key Error')
            continue
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return armature


def set_head_position(armature, verts, empties):
    if armature.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    try:
        head_bone = armature.data.edit_bones['mixamorig:Head']
    except KeyError:
        print("Error: 'mixamorig:Head' not found")
        return armature
    head_bone = armature.data.edit_bones['mixamorig:Head']
    y_list = []
    for i in verts:
        if i[2] > empties['mouth_centre'][2]:
            y_list.append(i[1])

    y_pos = sum(y_list) / len(y_list)
    length = head_bone.length
    head_bone.head = (empties['mouth_shoulder_centre'][0], y_pos, empties['mouth_centre'][2])
    head_bone.length = length
    head_bone.tail = (head_bone.head[0], head_bone.head[1], head_bone.head[2] + length)

    return armature

def set_neck_position(armature, empties):
    neck_bone = armature.data.edit_bones['mixamorig:Neck']
    neck_bone.head = (empties['mouth_shoulder_centre'][0], 
                      armature.data.edit_bones['mixamorig:Spine2'].tail[1], 
                      empties['mouth_shoulder_centre'][2])
    neck_bone.tail = (empties['mouth_shoulder_centre'][0], 
                      armature.data.edit_bones['mixamorig:Spine2'].tail[1], 
                      empties['mouth_centre'][2])

    return armature

def fix_foot_alignment(armature, empties, verts):
    for foot in ['Left', 'Right']:
        foot_bone = armature.data.edit_bones[f'mixamorig:{foot}Foot']
        foot_to_toe_bone = armature.data.edit_bones[f'mixamorig:{foot}ToeBase']
        roll1 = foot_bone.roll
        roll2 = foot_to_toe_bone.roll

        z_list = []
        for i in verts:
            if i[2] < empties[f'{foot.lower()}_heel'][2]:
                if i[1] < empties[f'{foot.lower()}_foot_index'][1]:
                    z_list.append(i[2])

        if z_list:  # Check if z_list is not empty
            z = sum(z_list) / len(z_list)
            foot_to_toe_bone.head[2] = z
            foot_to_toe_bone.tail[2] = z
            foot_bone.tail[2] = z
        else:
            print(f"Warning: z_list is empty for {foot} foot. Skipping foot alignment adjustment.")

        x1 = foot_bone.head[0]
        y1 = foot_bone.head[1]
        x2 = foot_to_toe_bone.tail[0]
        y2 = foot_to_toe_bone.tail[1]

        y = foot_to_toe_bone.head[1]
        x = ((y - y1) / (y2 - y1)) * (x2 - x1) + x1
        foot_bone.tail[0] = x
        foot_to_toe_bone.head[0] = x
        foot_bone.roll = roll1
        foot_to_toe_bone.roll = roll2

    return armature



def fix_arm_bone_roll(armature):
    armature.select_set(False)
    for bone in armature.data.edit_bones:
        if "Arm" in bone.name or "ForeArm" in bone.name:
            bone.select = True
    
    bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Z') 
    bpy.ops.object.editmode_toggle()
    bpy.context.object.show_in_front = True
    
    return armature


def snapSkeleton(filepath, empties, verts):
    armature = append_armature(filepath)
    bones_pos = get_bone_positions(armature, empties)
    spine_length = calculate_spine_length(armature, bones_pos, empties)
    armature = adjust_spine(armature, bones_pos, spine_length)
    armature = set_shoulder_positions(armature, empties)
    armature = set_head_position(armature, verts, empties)
    armature = set_neck_position(armature, empties)
    armature = fix_foot_alignment(armature, empties, verts)
    armature = fix_arm_bone_roll(armature)
    return armature


   
def create_empties(_file, centre_joints, filter_joints, verts):
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD',
                            location=(0,0,0), scale=(1,1,1))
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
            # print('yes')
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

def rig_mesh(armature_name, mesh_name):
    # Select the armature and mesh
    bpy.data.objects[armature_name].select_set(True)
    bpy.data.objects[mesh_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]

    # Parent the mesh to the armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Move the armature and mesh to a collection
    bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="rig")

    # Select the mesh
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=mesh_name, case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects[mesh_name]

    # Add a corrective smooth modifier
    bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
    bpy.context.object.modifiers["CorrectiveSmooth"].iterations = 100

def save_file(path, scan, mesh_name):
    # Save the file
    blend_file_path = os.path.join(path, scan, "photogrammetry")
    blend_file_name = f"{scan}-rig.blend"
    blend_file = os.path.join(blend_file_path, blend_file_name)
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)


def main():
    args = get_args()
    scan = str(args.scan)
    path = str(args.path)
    software_path = str(args.software)
    # Keypoints file
    keypoints_file_path = os.path.join(path, scan, "photogrammetry")
    keypoints_file_name = f"{scan}_results.txt"
    keypoints_file = os.path.join(keypoints_file_path, keypoints_file_name)

    # SCAN blend file
    obj_file_path = os.path.join(path, scan, "photogrammetry")
    obj_file_name = f"{scan}.blend"
    obj_file = os.path.join(obj_file_path, obj_file_name)

    # Blend file with reference skeleton
    blend_file_path = software_path
    blend_file_name = "skeleton_template_v03.blend"
    blend_file = os.path.join(blend_file_path, blend_file_name)

    bpy.ops.wm.append(
        filepath=obj_file,
        directory=os.path.join(obj_file_path, obj_file_name, "Collection/"),
        filename="geo"
    )
    obj = bpy.context.selected_objects[0]
    vertices = obj.data.vertices
    verts = [obj.matrix_world @ vert.co for vert in vertices]

    empties = create_empties(keypoints_file, CENTRE_JOINTS, FILTER_JOINTS, verts)

    snapSkeleton(os.path.join(blend_file_path,blend_file_name),empties, verts)

    rig_mesh("Armature", "g0")
    pack_textures()
    save_file(path, scan, "g0")

if __name__ == '__main__':
    main()


