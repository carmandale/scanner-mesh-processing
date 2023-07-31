import multiprocessing
import argparse
import bpy
import time
import math
import os

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
    parser.add_argument('-p', '--scans_path', help="scans directory", default="")
    parser.add_argument('-d', '--output_dir', help="output directory", default="") 
    parser.add_argument('-w', '--overwrite', help="overwrite turntables", default="0")
    parser.add_argument('-is', '--index_start', help="render from index", default="0")
    parser.add_argument('-ie', '--index_end', help="render to index", default="0")

    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# DEBUG
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


ST = time.perf_counter()
ET = time.perf_counter() - ST


# APPENDING
def append_scan(filepath, replace_obj_name = ""):
    directory = os.path.join(os.path.join(filepath, "Collection/"))
    
    # collection name
    collection_name = "geo"
        
    try:
        bpy.ops.wm.append(
        filepath=filepath,
        directory=directory,
        filename=collection_name)

        obj = bpy.context.scene.objects.get("g0")

        print_enhanced(f"The collection 'geo' from: {filepath}", label="APPENDED", label_color="green")

        if obj:
            if replace_obj_name != "":
                obj.name = replace_obj_name
                obj_col = bpy.data.collections.get("rig")
                if obj_col:
                    obj_col.name = replace_obj_name
            return obj
        return obj
    except Exception as e:
        print(f"--- ERROR: {e}")


# OBJECTS
def duplicate_object(obj):
    if obj is None:
        print_enhanced("reset_floor failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"duplicate_object | obj: {obj.name}", label="INFO", label_color="yellow")

    # Create a new object with the same data and properties
    duplicated_obj = obj.copy()
    duplicated_obj.data = obj.data.copy()
    
    # Link the duplicated object to the scene
    bpy.context.collection.objects.link(duplicated_obj)
    
    return duplicated_obj


def transform_object(obj, location=(0, 0, 0), rotation_degrees=(0, 0, 0), scale=(1, 1, 1)):
    if obj is None:
        print_enhanced("transform_object failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"transform_object | obj: {obj.name} | location: {location} | rotation_euler: {rotation_degrees} | scale: {scale}", label="INFO", label_color="yellow")

    obj.location = location
    obj.scale = scale

    if obj.rotation_mode == 'QUATERNION':
        obj.rotation_quaternion = rotation_degrees.to_quaternion()
        return
    
    obj.rotation_euler = (math.radians(rotation_degrees[0]), math.radians(rotation_degrees[1]), math.radians(rotation_degrees[2]))


def remove_object(obj):
    if obj is None:
        print_enhanced("remove_object failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if not obj.name in bpy.data.objects:
        print_enhanced("remove_object failed | obj.name not in bpy.data.objects", text_color="red", label="ERROR", label_color="red")
        return
    
    print_enhanced(f"remove_object | obj: {obj.name}", label="INFO", label_color="yellow")

    bpy.data.objects.remove(obj, do_unlink=True)


def apply_transform(obj, location=True, rotation=True, scale=True, properties=True):
    if obj is None:
        print_enhanced("apply_transform failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"apply_transform | obj: {obj.name} | location: {location} | rotation: {rotation} | scale: {scale} | properties: {properties}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj    
    obj.select_set(True)

    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale, properties=properties)


# OS
def find_directories(directory):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return [], []

    directories_paths = []
    directory_names = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            directories_paths.append(entry.path)
            directory_names.append(entry.name)

    return directories_paths, directory_names


def check_filepath_exists(filepath):
    """Check if a given filepath exists."""
    return os.path.exists(filepath)


# RENDERING
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


def change_render_format_to_jpeg(quality=90):

    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = quality


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


def set_scene_resolution(x=1080, y=1920):
    print_enhanced(f"Setting Scene Resolution | width: {x} | height: {y}", label="INFO", label_color="yellow")
    bpy.context.scene.render.resolution_x = x
    bpy.context.scene.render.resolution_y = y


def set_eevee_render_samples(value=16):
    print_enhanced(f"Setting EEVEE Render Samples | value: {value}", label="INFO", label_color="yellow")
    bpy.context.scene.eevee.taa_render_samples = value


def render_still(camera_obj, directory=None, filename=None, use_overwrite=True):
    if camera_obj is None:
        print_enhanced("render_and_save failed | camera_obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if directory is None or filename is None:
        print_enhanced("render_and_save failed | directory is None or filename is None", text_color="red", label="ERROR", label_color="red")
        return
    
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Set the active camera
    bpy.context.scene.camera = camera_obj

    # Set the output filepath
    filepath = os.path.join(directory, filename)
    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.render.use_overwrite = use_overwrite

    print_enhanced(f"Attempting to Render a Still Frame", label="INFO", label_color="yellow")
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print_enhanced(f"Rendering failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main(scan_ID, output_dir):
    print_decorated("Starting MAIN with a clean scene")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    print_enhanced("Creating World: START", label="INFO", label_color="yellow")
    bpy.ops.world.new()
    
    if not bpy.data.worlds:
        print_enhanced("World not found", label="ERROR", label_color="red")
        raise Exception
    
    bpy.context.scene.world = bpy.data.worlds[0]
    print_enhanced("Creating World: SUCCESS", label="INFO", label_color="yellow")

    # SCENE SETUP
    node_environment_image_path = "C:/RECURSOS/Textures/HDRI/HAVEN/kloofendal_48d_partly_cloudy_4k.hdr"
    add_hdr_environment(node_environment_image_path)
    camera = create_ortho_camera(location=(-0.5, -5.0, 1.04), rotation_in_degrees=(90, 0, 0), ortho_scale=5.87)
    change_render_format_to_jpeg(quality=80)
    set_scene_resolution(1920, 1080)
    set_eevee_render_samples(value=16)

    scan_blend_path = os.path.join(path, scan_ID, "photogrammetry", f"{scan_ID}.blend")
    scan_obj = append_scan(scan_blend_path)

    if scan_obj is None:
        return

    apply_transform(scan_obj)

    # fix texture patch
    image_filepath = os.path.join(path, scan_ID, "photogrammetry", "baked_mesh_tex0.png")
    if scan_obj.material_slots:
        if scan_obj.material_slots[0].material:
            if scan_obj.material_slots[0].material.node_tree.nodes["Image Texture"]:
                scan_obj.material_slots[0].material.node_tree.nodes["Image Texture"].image.filepath = image_filepath

    scan_obj_copy_0 = duplicate_object(scan_obj)
    scan_obj_copy_1 = duplicate_object(scan_obj)
    scan_obj_copy_2 = duplicate_object(scan_obj)

    transform_object(scan_obj_copy_0, location=(-2.55, 0, 1.25), rotation_degrees=(90, 0, 0))
    transform_object(scan_obj_copy_1, location=(-1.3, 0, 0), rotation_degrees=(0, 0, 108))
    transform_object(scan_obj_copy_2, location=(1.6, 0, 0), rotation_degrees=(0, 0, -162))

    render_still(camera, output_dir, f"{scan_ID}_turntable.jpg")

    print_enhanced(f"{scan_ID}", label=f"INDEX: {i} | RENDER FINISHED", label_color="green")


if __name__ == '__main__':
    # MAIN VARIABLES
    print_decorated("Main variables")

    args = get_args()
    path = str(args.scans_path)
    output_dir = str(args.output_dir)
    overwrite_files = str(args.overwrite)
    index_start = int(args.index_start)
    index_end = int(args.index_end)

    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(output_dir, label="OUTPUT_DIR", label_color="cyan")

    directories_data = find_directories(path)
    print_enhanced(directories_data[1], label="DIRECTORY_NAMES", label_color="cyan")

    if index_start < 0 or index_start >= len(directories_data[1]):
        index_start = 0

    if index_end <= 0 or index_end >= len(directories_data[1]):
        index_end = len(directories_data[1]) - 1

    # APPEND CHARACTER
    for i, scan_ID in enumerate (directories_data[1]):
        if any(word in scan_ID for word in ("turntable", "log", "test")):
            continue

        if i < index_start:
            continue

        if i > index_end + 1:
            break

        # To overwrite images or bypass the ones already created
        if overwrite_files == "0":
            if check_filepath_exists(os.path.join(output_dir, f"{scan_ID}_turntable.jpg")):
                continue

        main(scan_ID, output_dir)