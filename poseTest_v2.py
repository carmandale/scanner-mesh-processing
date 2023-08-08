import argparse
import shutil
import math
import bpy
import os
from mathutils import Vector
from typing import NamedTuple

print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬ poseTest_v2.py ▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ 07.27.2023 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ COMMAND LINE ARGUMENTS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# usage blender -b blender_filepath -P poseTest_v2_filepath -- --scan SCAN_ID --path SCAN_DIRECTORY --software SOFTWARE_DIRECTORY

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
    parser.add_argument('-cs', '--clean_start', help="to start with a clean scene", default=0)
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ DEBUG UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
use_debug = True


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


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ USEFUL FUNCTIONS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# OS
def save_as(filepath):
    try:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
    except Exception as e:
        print_enhanced(f"save_as failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


def copy_file(src_path, dst_path):
    try:
        shutil.copy(src_path, dst_path)
        print_enhanced("SUCCESS", label="COPY FILE", label_color="green")
        print_enhanced(f"{src_path}", label="FROM", label_color="cyan")
        print_enhanced(f"{dst_path}", label="TO", label_color="cyan", suffix="\n")
    except IOError as e:
        print_enhanced(f"Unable to copy file. {e}", text_color="red", label="IOError", label_color="red")
    except Exception as e:
        print_enhanced(f"Unable to copy file. {e}", text_color="red", label="Error", label_color="red")


# COLLECTIONS
def collection_link_object(obj, collection_name):
    if not isinstance(collection_name, str):
        return

    collection = bpy.data.collections.get(collection_name)
    
    # Check if the object and collection exist
    if not obj or not collection:
        return

    # Remove the object from its current collections
    for old_collection in obj.users_collection:
        old_collection.objects.unlink(obj)

    # Link the object to the specified collection
    collection.objects.link(obj)


def collection_find(name):
    """returns None if not found"""
    data = bpy.data
    collections = data.collections

    collection = None

    for collection in collections:
        if name == collection.name:
            print_enhanced(f"{collection.name}", label="FOUND COLLECTION", label_color="green")
            return collection


# OBJECTS
def object_set_transforms(obj, location=(0,0,0), rotation_euler=(0,0,0), rotation_quaternion=(1,0,0,0), scale=(1,1,1)):
    if obj is None:
        print_enhanced(f"object_set_transforms failed | obj is None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"object: {obj.name} | location: {location} | rotation_euler: {rotation_euler} | rotation_quaternion: {rotation_quaternion} | scale: {scale}", label="SET TRANSFORMS", label_color="green")
    
    obj.location = location
    obj.scale = scale
    
    if obj.rotation_mode != 'QUATERNION':
        obj.rotation_euler = tuple(math.radians(value) for value in rotation_euler)
        return
    
    obj.rotation_quaternion = rotation_quaternion


def create_cylinder(name, location, depth, radius=0.1):
    """Create a cylinder at a specified location"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        location=location,
    )
    cylinder = bpy.context.object
    cylinder.name = name
    return cylinder


def create_fake_bones(armature_name, bones_thickness=0.005, sphere_radius=0.0125, in_front=True):
    """
    Make armature's bones visible by representing them with cylinders
    """
    # Get the armature
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        print(f"No armature named '{armature_name}' found in the scene.")
        return
    
    # Create a temporary cylinder
    cylinder_mat_L = bpy.data.materials.get("cylinders_L")
    cylinder_mat_R = bpy.data.materials.get("cylinders_R")
    cylinder_mat_M = bpy.data.materials.get("cylinders_M")
    
    cylinder_temp = create_cylinder("cylinder_temp", Vector((0, 0, 0.5)), 1, bones_thickness)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    cylinder_temp.rotation_euler = (math.radians(-90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    cylinder_temp.show_in_front = in_front
    collection_link_object(cylinder_temp, collection_name="fake_bones")
    bpy.ops.object.material_slot_add()  
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=sphere_radius, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    sphere_temp = bpy.context.object
    sphere_temp.name = "sphere_temp"
    sphere_temp.show_in_front = in_front
    collection_link_object(sphere_temp, collection_name="fake_bones")

    sphere_mat = bpy.data.materials.get("spheres")
    if sphere_mat is not None:
        bpy.ops.object.material_slot_add()
        sphere_temp.material_slots[0].material = sphere_mat

    # Create a cylinder for each bone
    for bone in armature.pose.bones:
        # Duplicate the temporary cylinder
        bpy.ops.object.select_all(action='DESELECT')
        cylinder_temp.select_set(True)
        bpy.context.view_layer.objects.active = cylinder_temp
        bpy.ops.object.duplicate()
        cylinder = bpy.context.object
        cylinder.name = f"{bone.name}_cylinder"
        
        if cylinder_mat_M:
            cylinder.material_slots[0].material = cylinder_mat_M
        if "Left" in bone.name and cylinder_mat_L:
            cylinder.material_slots[0].material = cylinder_mat_L
        if "Right" in bone.name and cylinder_mat_R:
            cylinder.material_slots[0].material = cylinder_mat_R
        
        # Set up a copy rotation constraint so the cylinder follows the bone's rotation
        constraint = cylinder.constraints.new('COPY_LOCATION')
        constraint.target = armature
        constraint.subtarget = bone.name
        
        constraint = cylinder.constraints.new('COPY_ROTATION')
        constraint.target = armature
        constraint.subtarget = bone.name

        # Adjust the scale of the cylinder to match the bone's length
        cylinder.scale.y = bone.length

        bpy.ops.object.select_all(action='DESELECT')
        sphere_temp.select_set(True)
        bpy.context.view_layer.objects.active = sphere_temp
        bpy.ops.object.duplicate()
        sphere = bpy.context.object
        sphere.name = f"{bone.name}_sphere"
        
        constraint = sphere.constraints.new('COPY_LOCATION')
        constraint.target = armature
        constraint.subtarget = bone.name
        
    # Delete the temporary cylinder
    bpy.data.objects.remove(cylinder_temp)
    bpy.data.objects.remove(sphere_temp)


# RENDERING
def create_perspective_camera(location=(2.2, -4.8, 0.75), rotation_in_degrees=(92, 0, 24.5), lens=80, enter_editmode=False, align='VIEW'):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    rotation = tuple(math.radians(d) for d in rotation_in_degrees)
    bpy.ops.object.camera_add(enter_editmode=enter_editmode, align=align, location=location, rotation=rotation, scale=(1, 1, 1))
    camera_obj = bpy.context.object
    camera_obj.data.lens = lens
    print_enhanced(f"Perspective Camera Created | location={location} | rotation={rotation_in_degrees} | lens={lens}", label="INFO", label_color="yellow")
    return camera_obj


def set_scene_resolution(x=1080, y=1920):
    print_enhanced(f"Setting Scene Resolution | width: {x} | height: {y}", label="INFO", label_color="yellow")
    scene = bpy.context.scene
    scene.render.resolution_x = x
    scene.render.resolution_y = y


def render_still(camera, filepath, render_samples=16):
    if camera is None:
        if camera.type != 'CAMERA':
            print_enhanced("render_and_save failed | no camera", text_color="red", label="ERROR", label_color="red")
            return
        print_enhanced("render_and_save failed | no camera", text_color="red", label="ERROR", label_color="red")
        return
    
    if filepath == "":
        print_enhanced("render_and_save failed | no filepath", text_color="red", label="ERROR", label_color="red")
        return
    
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.eevee.taa_render_samples = render_samples

    print_enhanced(f"Attempting to Render a Still Frame", label="INFO", label_color="yellow", suffix="\n")
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print_enhanced(f"Rendering failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


# APPEND
def append_collection(filepath, collection_name):
    directory = os.path.join(os.path.join(filepath, "Collection/"))
    bpy.ops.wm.append(
    filepath=filepath,
    directory=directory,
    filename=collection_name)

    collection = collection_find(collection_name)
    if collection is None:
        print_enhanced(f"append_collection failed | collection is None", text_color="red", label="ERROR", label_color="red")
        return None
    
    print_enhanced(f"collection '{collection_name}' from {directory}", label="APPEND COLLECTION", label_color="green")
    return collection


class ScanRigs(NamedTuple):
    rig_0: bpy.types.Object
    rig_1: bpy.types.Object
    rig_2: bpy.types.Object


def append_scans(filepath):
    append_collection(filepath, "rig")
    append_collection(filepath, "rig")
    append_collection(filepath, "rig")
    scan_rig_0 = bpy.context.scene.objects.get("Armature")
    scan_rig_1 = bpy.context.scene.objects.get("Armature.001")
    scan_rig_2 = bpy.context.scene.objects.get("Armature.002")

    scan_rigs = ScanRigs(scan_rig_0, scan_rig_1, scan_rig_2)

    if scan_rigs.rig_0 is None or scan_rigs.rig_1 is None or scan_rigs.rig_2 is None:
        print_enhanced(f"append_scans failed | Missing one or more scan rigs", text_color="red", label="ERROR", label_color="red")
        return None

    if scan_rigs.rig_0.type != 'ARMATURE' or scan_rigs.rig_1.type != 'ARMATURE' or scan_rigs.rig_2.type != 'ARMATURE':
        print_enhanced(f"append_scans failed | One or more scan rigs are not type ARMATURE", text_color="red", label="ERROR", label_color="red")
        return None

    print_enhanced(f"{scan_rigs}", label="FOUND SCAN RIGS", label_color="cyan", suffix="\n")
    return scan_rigs 


class TestRigs(NamedTuple):
    rig_0: bpy.types.Object
    rig_1: bpy.types.Object


def append_test_rigs(filepath):
    collection = append_collection(filepath, "test_rigs")

    if collection is None:
        return None

    test_rig_0 = bpy.context.scene.objects.get("test_rig_0")
    test_rig_1 = bpy.context.scene.objects.get("test_rig_1")

    if test_rig_0 is None or test_rig_1 is None:
        print_enhanced(f"append_test_rig failed | Missing one or more test rigs", text_color="red", label="ERROR", label_color="red")
        return None

    if test_rig_0.type != 'ARMATURE' or test_rig_1.type != 'ARMATURE':
        print_enhanced(f"append_test_rig failed | One or more test rigs are not type ARMATURE", text_color="red", label="ERROR", label_color="red")
        return None

    print_enhanced(f"{test_rig_0.name} | {test_rig_1.name}", label="FOUND TEST RIGS", label_color="cyan", suffix="\n")

    return TestRigs(test_rig_0, test_rig_1)

# SCENE
def scene_clean_start():
    print_decorated("Starting MAIN with a clean scene")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    print_enhanced("Creating World: START", label="INFO", label_color="yellow")
    bpy.ops.world.new()

    if not bpy.data.worlds:
        print_enhanced("World not found", label="ERROR", label_color="red")
        raise Exception

    bpy.context.scene.world = bpy.data.worlds[0]
    print_enhanced("Creating World: SUCCESS", label="INFO", label_color="yellow")


# RETARGETING
def pose_bone_add_constraint(bone, target, subtarget="", clear_constraints=True, type='COPY_ROTATION', use_offset=False):
    if not bone:
        return False

    if clear_constraints and len(bone.constraints) > 0:
        constraints = [c for c in bone.constraints]
        for constraint in constraints:
            bone.constraints.remove(constraint)

    new_constraint = bone.constraints.new(type)
    if new_constraint is None:
        return False
    
    new_constraint.target = target
    new_constraint.subtarget = subtarget
    new_constraint.use_offset = use_offset
    return True


def pose_bones_apply_all_constraints(armature, exclude_list=[]):
    if armature is None:
        print_enhanced("pose_bones_apply_all_constraints failed | armature is None", label="ERROR", label_color="red")
        return

    if armature.type != 'ARMATURE':
        print_enhanced("pose_bones_apply_all_constraints failed | armature != 'ARMATURE'", label="ERROR", label_color="red")
        return
    
    print_enhanced("Applying all bone constraints", label=f"{armature.name}", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    for bone in armature.pose.bones:
        bpy.context.object.data.bones.active = bone.bone
        constraints = [c for c in bone.constraints]
        if constraints:
            for c in constraints:
                if exclude_list:
                    if c.name in exclude_list:
                        continue
                bpy.ops.constraint.apply(constraint=c.name, owner='BONE', report=False)

    bpy.ops.object.mode_set(mode='OBJECT')


def retarget_target_bones(target_armature, bones_to_retarget):
    for bone in bones_to_retarget:
        pose_bone_add_constraint(bone, target=target_armature, subtarget=bone.name)


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main():

    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN VARIABLES ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    print_decorated("MAIN VARIABLES")

    args = get_args()
    path = str(args.path)
    scan_ID = str(args.scan)
    use_clean_start = int(args.clean_start)
    software_path = str(args.software)
    
    rig_filepath = os.path.join(path, scan_ID, "photogrammetry", f"{scan_ID}-rig.blend")
    pose_test_rig_filename = "pose_test_rig_v01.blend"
    pose_test_rig_filepath = os.path.join(software_path, pose_test_rig_filename)

    pose_test_blender_filepath = os.path.join(path, scan_ID, "photogrammetry", f"{scan_ID}-pose_test.blend")
    fake_bones_render_filepath = os.path.join(path, scan_ID, "photogrammetry", f"{scan_ID}-pose_test_bones.png")
    pose_test_render_filepath = os.path.join(path, scan_ID, "photogrammetry", f"{scan_ID}-pose_test.png")
    _pose_test_render_filepath = os.path.join(path, "_pose_test", f"{scan_ID}-pose_test.png")

    print_enhanced(f"{path}", label="PATH", label_color="cyan")
    print_enhanced(f"{scan_ID}", label="SCAN", label_color="cyan")
    print_enhanced(f"{use_clean_start}", label="USE CLEAN START", label_color="cyan")
    print_enhanced(f"{software_path}", label="SOFTWARE PATH", label_color="cyan")
    print_enhanced(f"{rig_filepath}", label="RIG FILEPATH", label_color="cyan")
    print_enhanced(f"{pose_test_rig_filepath}", label="TEST RIG FILEPATH", label_color="cyan")

    bones_to_retarget_names = [
    "mixamorig:RightArm",
    "mixamorig:LeftArm",
    "mixamorig:RightForeArm",
    "mixamorig:LeftForeArm",
    "mixamorig:RightHand",
    "mixamorig:LeftHand",
    "mixamorig:LeftShoulder",
    "mixamorig:RightShoulder",
    "mixamorig:RightUpLeg",
    "mixamorig:LeftUpLeg",
    "mixamorig:RightLeg",
    "mixamorig:LeftLeg",
    "mixamorig:Spine",
    "mixamorig:Spine1",  
    "mixamorig:Spine2",  
    ]

    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN STEPS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    print_decorated("MAIN STEPS")

    if use_clean_start:
        scene_clean_start()

    scan_rigs = append_scans(rig_filepath)
    test_rigs = append_test_rigs(pose_test_rig_filepath)

    if scan_rigs is None:
        print_enhanced("Main Failed | scan_rigs is None", text_color="red", label="ERROR", label_color="red")
        return

    if test_rigs is None:
        print_enhanced("Main Failed | test_rigs is None", text_color="red", label="ERROR", label_color="red")
        return

    scan_rig_0_bones_to_retarget = []
    for i in range(0, len(bones_to_retarget_names)):
        scan_rig_0_bones_to_retarget.append(scan_rigs.rig_0.pose.bones.get(bones_to_retarget_names[i]))

    scan_rig_1_bones_to_retarget = []
    for i in range(0, len(bones_to_retarget_names)):
        scan_rig_1_bones_to_retarget.append(scan_rigs.rig_1.pose.bones.get(bones_to_retarget_names[i]))

    retarget_target_bones(test_rigs.rig_0, scan_rig_0_bones_to_retarget)
    retarget_target_bones(test_rigs.rig_1, scan_rig_1_bones_to_retarget)

    constraints_exclude_list = ["Limit Location", "Limit Rotation"]
    pose_bones_apply_all_constraints(scan_rigs.rig_0, constraints_exclude_list)
    pose_bones_apply_all_constraints(scan_rigs.rig_1, constraints_exclude_list)

    object_set_transforms(scan_rigs.rig_1, (2.4, 0, 0), (0, 0, -74))
    object_set_transforms(scan_rigs.rig_2, (1.32, 0, 0), (0, 0, 22))

    scan_meshes = [obj for obj in bpy.context.scene.objects if "g0" in obj.name]

    if not scan_meshes:
        print_enhanced("Main Failed | scan_meshes = []", text_color="red", label="ERROR", label_color="red")
        return

    scan_meshes_modifiers = [modifier for modifier in [obj for obj in scan_meshes]]
    if scan_meshes_modifiers:
        for modifier in scan_meshes_modifiers:
            if modifier.name == "CorrectiveSmooth":
                modifier.iterations = 7

    scan_rig_collections = [collection_find("rig"), collection_find("rig.001"), collection_find("rig.002")]
    fake_bones_collection = collection_find("fake_bones")

    # CREATE FAKE BONES
    create_fake_bones(scan_rigs.rig_0.name)
    create_fake_bones(scan_rigs.rig_1.name)
    create_fake_bones(scan_rigs.rig_2.name)

    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ RENDERING & SAVING ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    print_decorated("RENDERING & SAVING")

    camera = create_perspective_camera(location=(5.05, -8.4, 0.6), rotation_in_degrees=(92, 0 , 24.5))
    set_scene_resolution(1920, 1080)

    for scan_rig_collection in scan_rig_collections:
        scan_rig_collection.hide_render = True
    fake_bones_collection.hide_render = False
    bpy.context.scene.render.film_transparent = True

    if not bpy.context.scene.node_tree.nodes.get("Alpha Over"):
        print_enhanced("Compositor node 'Alpha Over' missing", text_color="red", label="ERROR", label_color="red")
        return
    
    bpy.context.scene.node_tree.nodes["Alpha Over"].inputs[0].default_value = 0

    render_still(camera, fake_bones_render_filepath)

    if bpy.data.images.get("bones_image"):
        bpy.data.images['bones_image'].filepath = fake_bones_render_filepath

    for scan_rig_collection in scan_rig_collections:
        scan_rig_collection.hide_render = False
    fake_bones_collection.hide_render = True
    bpy.context.scene.render.film_transparent = False

    bpy.context.scene.node_tree.nodes["Alpha Over"].inputs[0].default_value = 0.75

    render_still(camera, pose_test_render_filepath)
    copy_file(pose_test_render_filepath, _pose_test_render_filepath)
    save_as(pose_test_blender_filepath)


if __name__ == '__main__':
    main()