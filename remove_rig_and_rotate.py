import os
import bpy
import math
import shutil
import argparse


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬ REMOVE RIG AND ROTATE ▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 8.23.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


# usage blender -b SCAN_ID-rig.blend -P remove_rig_and_rotate.py -- --scan SCAN_ID --path SCAN_DIRECTORY --software SOFTWARE_DIRECTORY


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
    parser.add_argument('-m', '--path', help="directory", default="/System/Volumes/Data/mnt/scanDrive/takes/") 
    parser.add_argument('-s', '--software', help="software", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/")
    parser.add_argument('-env', '--environment_map', help="hdri texture", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr")
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


def remove_object(obj):
    if obj is None:
        print_enhanced("remove_object failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if not obj.name in bpy.data.objects:
        print_enhanced("remove_object failed | obj.name not in bpy.data.objects", text_color="red", label="ERROR", label_color="red")
        return
    
    print_enhanced(f"remove_object | obj: {obj.name}", label="INFO", label_color="yellow")

    bpy.data.objects.remove(obj, do_unlink=True)


def remove_all_modifiers(obj):
    if not obj:
        print_enhanced(f"remove_all_modifiers failed | object not found", text_color="red", label="ERROR", label_color="red")
        return

    if obj.modifiers:
        while len(obj.modifiers) > 0:
            print_enhanced(f"{obj.modifiers[0].name}", label="REMOVE MODIFIER", label_color="red")
            obj.modifiers.remove(obj.modifiers[0])


def remove_collection(collection_name, remove_all_objects=True):
    collection = bpy.data.collections.get(collection_name)

    if collection:
        if remove_all_objects:
            for obj in collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.collections.remove(collection)
        print_enhanced(f"{collection_name}", label="REMOVING COLLECTION", label_color="yellow")


def collection_change_name(collection_name, new_name):
    collection = bpy.data.collections.get(collection_name)

    if collection is None:
        print_enhanced(f"collection_change_name failed | collection not found", text_color="red", label="ERROR", label_color="red")
        return

    collection.name = new_name
    print_enhanced(f"Changed '{collection_name}' name to: {new_name}", label="INFO", label_color="yellow")


def object_remove_all_vertex_groups(obj):
    if obj is None:
        print_enhanced("object_remove_all_vertex_groups FAILED | obj is None", text_color_code="red", label="ERROR", label_color_code="red")
        return

    if obj.type != 'MESH':
        print_enhanced("object_remove_all_vertex_groups FAILED | obj.type != 'MESH'", text_color_code="red", label="ERROR", label_color_code="red")
        return

    vertex_groups = obj.vertex_groups
    if vertex_groups:
        for vert_group in vertex_groups:
            vertex_groups.remove(vert_group)


def add_hdr_environment(image_path):
    print_enhanced(f"Adding HDR Environment | path: {image_path}", label="INFO", label_color="yellow")
    context = bpy.context
    scene = context.scene

    # Get the environment node tree of the current scene
    node_tree = scene.world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(image_path) # Relative path
    node_environment.location = -300,0

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 200,0

    # Link all nodes
    links = node_tree.links
    links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    links.new(node_background.outputs["Background"], node_output.inputs["Surface"])


def pack_textures():
    print_enhanced(f"pack_textures", label="INFO", label_color="yellow")
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            print_enhanced(f"{image.name}", label="PACKING IMAGE", label_color="green")
            image.pack()


def set_scene_resolution(x=1080, y=1920):
    print_enhanced(f"Setting Scene Resolution | width: {x} | height: {y}", label="INFO", label_color="yellow")
    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920


def create_ortho_camera(location=(0, -1.56, 0.8762), rotation_in_degrees=(90, 0, 0), ortho_scale=2.3, enter_editmode=False, align='VIEW'):
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    rotation = tuple(math.radians(d) for d in rotation_in_degrees)
    bpy.ops.object.camera_add(enter_editmode=enter_editmode, align=align, location=location, rotation=rotation, scale=(1, 1, 1))
    obj = bpy.context.object
    obj.data.type = 'ORTHO'
    obj.data.ortho_scale = ortho_scale
    print_enhanced(f"Orthographic Camera Created | location={location} | rotation={rotation_in_degrees}", label="INFO", label_color="yellow")
    return obj


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
    software = str(args.software)
    environment_map = str(args.environment_map)

    print_decorated("Command line Arguments")
    print_enhanced(scan, label="SCAN", label_color="cyan")
    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(software, label="SOFTWARE", label_color="cyan")
    print_enhanced(environment_map, label="ENVIRONMENT MAP", label_color="cyan")

    # REMOVE RIG
    print_decorated("Remove Rig")
    obj = get_object('g0')
    if obj is None:
        print_enhanced("Remove Rig FAILED | g0 not found", label="ERROR", label_color="red")
        return
    remove_all_modifiers(obj)

    armature = get_object('Armature')
    if armature is None:
        print_enhanced("Remove Rig FAILED | Armature not found", label="ERROR", label_color="red")
        return
    remove_object(armature)
    object_remove_all_vertex_groups(obj)

    print_decorated("Rotate Mesh")
    set_object_transforms(obj, rotation_euler=(0, 0, math.radians(180)))
    apply_object_transforms(obj, rotation=True)

    # ORGANIZE
    print_decorated("Organizing")
    remove_collection("keypoints", remove_all_objects=True)
    remove_collection("keypoints_front", remove_all_objects=True)
    collection_change_name(collection_name="rig", new_name="geo")

    # RENDERING AND SAVING
    print_decorated("Rendering and Saving")

    # Textures and Camera
    add_hdr_environment(image_path=environment_map)
    pack_textures()
    camera = create_ortho_camera(location=(0, -1.56, 0.8762), rotation_in_degrees=(90, 0, 0), ortho_scale=2.3)
    set_scene_resolution(x=1080, y=1920)
    render_output_path = os.path.join(path, scan, "photogrammetry", f"{scan}.png")
    new_blend_filepath = os.path.join(path, str(scan), "photogrammetry", f"{scan}.blend")
    render_and_save(obj, camera, render_output_path, new_blend_filepath)


if __name__ == '__main__':
    main()