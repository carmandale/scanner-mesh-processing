import argparse
import bpy
import bmesh
import math
import numpy
import time
import os
from mathutils import Vector


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬ Render Image for Face Detection ▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 9.20.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


# Usage: blender -b SCAN_ID.blend -P render_image_for_face_detection.py -- --scan SCAN_ID --path SCAN_DIRECTORY


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
    parser.add_argument('-env', '--environment_map', help="hdri texture", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ DEBUG UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
use_debug = True

def repeat_string(string, amount):
        concatenated_string = string * amount
        return concatenated_string


def debug_function_execution_with_args(func):
    def wrapper(*args, **kwargs):
        func_name = f"{func.__name__}()".upper()

        if not use_debug:
             return func(*args, **kwargs)
        
        start_label = f"\n▬▬▬ {func_name}: START ▬▬▬"        
        print(start_label)
        print (repeat_string("▬", len(start_label) - 1))

        print(f"▬▬▬ ARGS")

        if not args:
            print ("▬▬▬▬▬▬", None)
            
        for arg in args:
            print ("▬▬▬▬▬▬", arg)

        print(f"▬▬▬ KEYWORD ARGS")
        for key, value in kwargs.items():
            print("▬▬▬▬▬▬", key, ":", value)
    
        print(f"▬▬▬ RETURN ◄")
        result = func(*args, **kwargs)

        print("▬▬▬▬▬▬", result)

        end_label = f"▬▬▬ {func_name}: END ▬▬▬"
        print (repeat_string("▬", len(end_label) - 1))
        print(end_label)
        
        return result
    return wrapper


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

def select_all_objects(action='SELECT'):
    """
    Select all objects in the current scene while in Object mode.

    action (str): Valid values are 'SELECT' and 'DESELECT'.

    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action=action)

def set_object_mode(mode='OBJECT'):
    bpy.ops.object.mode_set(mode=mode)


def pack_textures():
    print_enhanced(f"pack_textures", label="INFO", label_color="yellow")
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            print_enhanced(f"{image.name}", label="PACKING IMAGE", label_color="green")
            image.pack()


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


def set_scene_resolution(x=1080, y=1920):
    print_enhanced(f"Setting Scene Resolution | width: {x} | height: {y}", label="INFO", label_color="yellow")
    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920


def apply_transform(obj, location=True, rotation=True, scale=True, properties=True):
    if obj is None:
        print_enhanced("rotate_object_to_rotation_quaternion failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"apply_transform | obj: {obj.name} | location: {location} | rotation: {rotation} | scale: {scale} | properties: {properties}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj    
    obj.select_set(True)

    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale, properties=properties)


def file_exists(filepath):
    return os.path.isfile(filepath)


def create_material(material_name, texture_path):
    if not file_exists(texture_path):
        print_enhanced(f"create_material failed | texture_path: {texture_path} doesn't exists", text_color="red", label="ERROR", label_color="red")
        return
    #STAGE 5: Create Material
    data = bpy.data
    mat = data.materials.new(name=material_name)
    tex = data.textures.new("diffuse", 'IMAGE')

    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = data.images.load(texture_path)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    mat.node_tree.links.new(bsdf.inputs['Emission'], texImage.outputs['Color'])
    
    # specular
    bsdf.inputs[9].default_value = 1
    # roughness
    bsdf.inputs[7].default_value = 0
    # emission
    bsdf.inputs[20].default_value = 0.5

    return mat

def add_material_to_object(obj, material):
    if obj is None:
        print_enhanced("add_material_to_object failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    obj.data.materials.append(material)


def sort_by_vertex_count(obj):
    return len(obj.data.vertices)


def mesh_cleanup(mesh_obj):
    # Convert the object to a mesh and create a BMesh
    me = mesh_obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    # Filter out vertices with too many linked faces
    cleaned_verts = [v for v in bm.verts if len(v.link_faces) <= 30]

    # Delete vertices that don't meet the criteria
    for v in bm.verts:
        if v not in cleaned_verts:
            bmesh.ops.delete(bm, geom=[v], context='VERTS')

    # Update the mesh with the modified BMesh
    bm.to_mesh(me)
    me.update()
    
    # Cleanup
    bm.free()


def close_mesh_holes(mesh_obj):
    if mesh_obj is None:
        print_enhanced("close_mesh_holes failed | mesh_obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    print_enhanced(f"close_mesh_holes | mesh_obj: {mesh_obj}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # Switch to Edit mode and select all vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Fill holes in the mesh
    bpy.ops.mesh.fill_holes(sides=0)

    # Triangulate new faces
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')


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


def find_connected_face_components(bmesh_obj):
    """Yields sets of faces which are connected components"""
    remaining_faces = set(bmesh_obj.faces)
    while remaining_faces:
        current_faces = {remaining_faces.pop()}
        connected_faces = set()
        while current_faces:
            face = current_faces.pop()
            connected_faces.add(face)
            current_faces |= {linked_face for edge in face.edges for linked_face in edge.link_faces} - connected_faces
        yield connected_faces
        remaining_faces -= connected_faces


def remove_loose_geometry(obj, remove_vertices=True, remove_edges=True, remove_faces=True, remove_linked_faces=False, max_linked_faces=None):
    if obj is None:
        print_enhanced("remove_loose_geometry failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"remove_loose_geometry | obj: {obj.name} | remove_vertices: {remove_vertices} | remove_edges: {remove_edges} | remove_faces: {remove_faces} | remove_linked_faces: {remove_linked_faces} | max_linked_faces: {max_linked_faces}", label="INFO", label_color="yellow")

    bmesh_obj = bmesh.new()
    bmesh_obj.from_mesh(obj.data)

    if remove_faces:
        loose_faces = [face for face in bmesh_obj.faces if all(len(edge.link_faces) == 1 for edge in face.edges)]
        print_enhanced(f"removed {len(loose_faces)}", label="LOOSE FACES", label_color="magenta")
        bmesh.ops.delete(bmesh_obj, geom=loose_faces, context='FACES')

    if remove_edges:
        loose_edges = [edge for edge in bmesh_obj.edges if not edge.link_faces]
        print_enhanced(f"removed {len(loose_edges)}", label="LOOSE EDGES", label_color="magenta")
        bmesh.ops.delete(bmesh_obj, geom=loose_edges, context='EDGES')

    if remove_vertices:
        loose_verts = [vertex for vertex in bmesh_obj.verts if not vertex.link_edges]
        print_enhanced(f"removed {len(loose_verts)}", label="LOOSE VERTS", label_color="magenta")
        bmesh.ops.delete(bmesh_obj, geom=loose_verts, context='VERTS')

    if remove_linked_faces and max_linked_faces is not None:
        for connected_faces in find_connected_face_components(bmesh_obj):
            if len(connected_faces) < max_linked_faces:
                print_enhanced(f"removed with {len(connected_faces)} faces", label="LOOSE LINKED FACES", label_color="magenta")
                bmesh.ops.delete(bmesh_obj, geom=list(connected_faces), context='FACES')

    bmesh_obj.to_mesh(obj.data)
    bmesh_obj.free()


def remove_doubles_bmesh(obj, merge_distance=0.001):
    """ Merge by distance. Works in OBJECT mode."""

    if obj is None:
        print_enhanced("remove_doubles_bmesh failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"remove_doubles_bmesh | scan_obj: {obj.name} | merge_distance: {merge_distance}", label="INFO", label_color="yellow")

    # Ensure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Create a BMesh from the object mesh data
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Remove doubles
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)

    # Write the BMesh back to the object mesh
    bm.to_mesh(mesh)
    bm.free()


def render_and_save(obj, camera_obj, output_path):
    # Set the object location to (0, 0, 0)
    if obj is None:
        print_enhanced("render_and_save failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if camera_obj is None:
        print_enhanced("render_and_save failed | camera_obj = None", text_color="red", label="ERROR", label_color="red")
        return
    
    if output_path == "":
        print_enhanced("render_and_save failed | output_path = N/A", text_color="red", label="ERROR", label_color="red")
        return
    
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    #  Make sure the object is at the origin
    obj.location = (0, 0, 0)

    # Set the active camera
    bpy.context.scene.camera = camera_obj

    # Set the output file path
    bpy.context.scene.render.filepath = output_path

    print_enhanced(f"Attempting to Render a Still Frame", label="INFO", label_color="yellow")
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print_enhanced(f"Rendering failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")

    print_enhanced(f"Attempting to Save the File", label="INFO", label_color="yellow")
    try:
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print_enhanced(f"Save File failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


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


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main():
    # HERE: COMMAND LINE ARGS
    print_decorated("Command line Arguments")

    args = get_args()
    scan = str(args.scan)
    path = str(args.path)
    environment_map = str(args.environment_map)

    print_enhanced(scan, label="SCAN", label_color="cyan")
    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(environment_map, label="ENVIRONMENT MAP", label_color="cyan")

    # HERE: MAIN VARIABLES
    print_decorated("Main variables")

    texture_path = os.path.join(path, str(scan), "photogrammetry", "baked_mesh_tex0.png")
    material_name = "MAT"

    print_enhanced(texture_path, label="SCAN TEXTURE PATH", label_color="cyan")
    print_enhanced(material_name, label="MATERIAL NAME", label_color="cyan")

    # HERE: SCENE SETUP
    print_decorated("Setting up the mesh")

    scan_obj = bpy.context.scene.objects.get('g0')

    if scan_obj is None:
        print_enhanced("CANCELLED | scan_obj not found", text_color="red", label="ERROR", label_color="red")
        return

    scan_obj_material = create_material(material_name, texture_path)
    add_material_to_object(scan_obj, scan_obj_material)

    # HERE: CLEANING
    print_decorated("Cleaning")

    remove_loose_geometry(scan_obj, remove_linked_faces=True, max_linked_faces=200)
    close_mesh_holes(scan_obj)
    remove_doubles_bmesh(scan_obj)

    # Textures and Camera
    add_hdr_environment(image_path=environment_map)
    pack_textures()
    
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']

    if cameras:
        camera = cameras[0]
    else:
        camera = create_ortho_camera(location=(0, -1.56, 0.8762), rotation_in_degrees=(90, 0, 0), ortho_scale=2.3)

    # HERE: RENDERING AND SAVING
    print_decorated("Rendering and Saving")

    set_scene_resolution(x=1080, y=1920)
    render_output_path = os.path.join(path, str(scan), "photogrammetry", f"{scan}.png")
    render_and_save(scan_obj, camera, render_output_path)

    return scan

if __name__ == '__main__': 
    IT = time.perf_counter()

    scan_ID = main()

    ET_S = time.perf_counter() - IT
    print_enhanced(f"Total Elapsed Time: {ET_S} sec", label=f"ID: {scan_ID} | CleanUp_v3 FINISHED", label_color="green")