import os
import bpy
import math
import shutil
import argparse


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ ROTATE MESH ▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 8.22.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
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
    script_args = all_arguments[double_dash_index + 1:]
    
    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default="/Users/administrator/groove-test/takes/") 
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ DEBUG UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

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

def move_and_rename_file(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)


def get_object(name):
    return bpy.context.scene.objects.get(name)


def select_object (name):
    obj = bpy.context.scene.objects.get(name)
    if obj is None:
        print_enhanced(f"select_object failed | object: {name} not found", text_color="red", label="ERROR", label_color="red")
        return

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = obj    
    obj.select_set(True)

    return obj


def set_object_transforms(obj, location=(0,0,0), rotation_euler=(0,0,0), rotation_quaternion=(1,0,0,0), scale=(1,1,1)):
    if not obj:
        return
    print_enhanced(f"object: {obj.name} | location: {location} | rotation_euler: {rotation_euler} | rotation_quaternion: {rotation_quaternion} | scale: {scale}", label="SET TRANSFORMS", label_color="green")

    obj.location = location
    obj.scale = scale

    if obj.rotation_mode != 'QUATERNION':
        obj.rotation_euler = rotation_euler
        return

    obj.rotation_quaternion = rotation_quaternion


def apply_object_transforms(obj, location=False, rotation=False, scale=False, clear_rotations=False):
    if not obj:
        return
    print_enhanced(f"object: {obj.name} | location: {location} | rotation: {rotation} | scale: {scale} | clear_rotations: {clear_rotations}", label="APPLY TRANSFORM", label_color="green")

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Clear rotations if specified
    if clear_rotations:
        bpy.ops.object.rotation_clear()

    # Apply all transformations
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def set_scene_resolution(x=1080, y=1920):
    print_enhanced(f"Setting Scene Resolution | width: {x} | height: {y}", label="INFO", label_color="yellow")
    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920


def render_and_save(obj, camera_obj, render_output_path, save_filepath):
    # Set the object location to (0, 0, 0)
    if obj is None:
        print_enhanced("render_and_save failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if camera_obj is None:
        print_enhanced("render_and_save failed | camera_obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if render_output_path == "":
        print_enhanced("render_and_save failed | output_path = N/A", text_color="red", label="ERROR", label_color="red")
        return
    
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    #  Make sure the object is at the origin
    obj.location = (0, 0, 0)

    # Set the active camera
    bpy.context.scene.camera = camera_obj

    # Set the output file path
    bpy.context.scene.render.filepath = render_output_path

    print_enhanced(f"Attempting to Render a Still Frame", label="INFO", label_color="yellow")
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print_enhanced(f"Rendering failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")

    print_enhanced(f"Attempting to Save the File", label="INFO", label_color="yellow")
    try:
        bpy.ops.wm.save_mainfile(filepath=save_filepath)
    except Exception as e:
        print_enhanced(f"Save File failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


def main():
    args = get_args()
    scan = str(args.scan)
    path = str(args.path)

    print_decorated("Command line Arguments")
    print_enhanced(scan, label="SCAN", label_color="cyan")
    print_enhanced(path, label="PATH", label_color="cyan")

    # ROTATE 180 AND APPLY ROTATION
    print_decorated("Rotate 180° and Apply Rotation")
    obj = get_object('g0')
    set_object_transforms(obj, rotation_euler=(0, 0, math.radians(180)))
    apply_object_transforms(obj, rotation=True)

    # RENDERING AND SAVING
    print_decorated("Rendering and Saving")

    set_scene_resolution(x=1080, y=1920)
    camera = bpy.context.scene.objects.get("Camera")
    render_output_path = os.path.join(path, scan, "photogrammetry", f"{scan}.png")
    new_blend_filepath = os.path.join(path, str(scan), "photogrammetry", f"{scan}.blend")
    render_and_save(obj, camera, render_output_path, new_blend_filepath)


if __name__ == '__main__':
    main()