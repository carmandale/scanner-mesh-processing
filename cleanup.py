import argparse
import bpy
import bmesh
import math
import numpy
import time
import os
from mathutils import Vector, Euler, Matrix, Quaternion


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ Clean Up ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 07.18.25 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n')


# v2.0.1 based on Stripper_v18
# edited by Dale Carman on 02.20.23
# edited by Luis Pineda on July 2023
# edited by Luis Pineda on July 2025 to fix the usda import and
# to add new functions to find the floor and to extract it from the scan mesh


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
    parser.add_argument('-p', '--padding', help="padding", default=0.0) 
    parser.add_argument('-f', '--floor_height', help="floor_height", default=0.001) 
    parser.add_argument('-r', '--facing', help="facing", default=0.5)
    parser.add_argument('-cs', '--clean_start', help="to start with a clean scene", default=1)
    parser.add_argument('-uc1', '--use_cleaning_1', help="Use Cleaning 1", default="1")
    parser.add_argument('-uc2', '--use_cleaning_2', help="Use Cleaning 2", default="1")
    parser.add_argument('-uo', '--use_orientation', help="Use Orientation", default="1")
    parser.add_argument('-ores', '--output_resolution', help="Output Resolution: 'W_H'", default="1080_1920")
    parser.add_argument('-env', '--environment_map', help="hdri texture", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr")
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

def create_cube_in_editmode(obj, location=(0,0,0), rotation=(0,0,0), scale=(0,0,0), enter_editmode=False, align='WORLD'):
    if obj is None:
        print_enhanced("create_cube_in_editmode failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    if bpy.context.object:
        if bpy.context.object.name != obj.name:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation, scale=scale, enter_editmode=enter_editmode, align=align)
    print_enhanced(f"create_cube_in_editmode | location: {location} | rotation: {rotation} | scale: {scale}", label="INFO", label_color="yellow")


def add_solidify_modifier(obj, thickness=0.01, output_shell_vertex_group=True):
    """
    return: solidify modifier, if output_shell_vertex_group=True also returns shell_vertex_group.name else None
    """
    if obj is None:
        print_enhanced("add_solidify_modifier failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"add_solidify_modifier | obj: {obj.name} | thickness: {thickness} | output_shell_vertex_group: {output_shell_vertex_group}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    solidify_modifier = None
    bpy.ops.object.modifier_add(type='SOLIDIFY')

    if obj.modifiers:
        solidify_modifier = obj.modifiers.get("Solidify")
        if solidify_modifier:
            solidify_modifier.thickness = thickness
            if output_shell_vertex_group:
                shell_vertex_group = obj.vertex_groups.new(name="solidify_shell")
                solidify_modifier.shell_vertex_group = shell_vertex_group.name
                return solidify_modifier, shell_vertex_group.name
            return solidify_modifier, None
        

def select_vertex_group_vertices(obj, vertex_group_name, delete_selected_faces=False, invert_selection=False):
    if obj is None:
        print_enhanced("select_vertex_group_vertices failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"select_vertex_group_vertices | obj: {obj.name} | vertex_group_name: {vertex_group_name}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    vertex_group = obj.vertex_groups.get(vertex_group_name)

    if not vertex_group:
        print_enhanced(f"select_vertex_group_vertices failed | vertex_group '{vertex_group_name}' not found", text_color="red", label="ERROR", label_color="red")
        return

    for vertex in obj.data.vertices:
        for group in vertex.groups:
            if group.group == vertex_group.index:
                vertex.select = True

    if delete_selected_faces:
        bpy.ops.object.mode_set(mode='EDIT')

        if invert_selection:
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='FACE')
            print_enhanced(f"Selected vertices of: {vertex_group_name} and deleted the faces after inverting the selection", label="VERTEX GROUP", label_color="green")

        bpy.ops.mesh.delete(type='FACE')
        print_enhanced(f"Selected vertices of: {vertex_group_name} and deleted the faces", label="VERTEX GROUP", label_color="green")

        return

    print_enhanced(f"Selected vertices of: {vertex_group_name}", label="VERTEX GROUP", label_color="green")


def apply_all_modifier(obj):
    if obj is None:
        print_enhanced("apply_all_modifier failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"apply_all_modifier | obj: {obj.name}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    while len(obj.modifiers) > 0:
        modifier = obj.modifiers[0]
        print_enhanced(f"Modifier: {modifier.name}", label="APPLYING", label_color="green")
        bpy.ops.object.modifier_apply(modifier=modifier.name)


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


def join_objects(target_obj, objs_to_join):
    if target_obj is None or not objs_to_join:
        print_enhanced("join_objects failed | obj = None or not objs_to_join", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"join_objects | target_obj: {target_obj.name} | objs_to_join: {objs_to_join}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs_to_join:
        if target_obj.type == 'MESH' and obj.type == 'MESH':
            obj.select_set(True)
        if target_obj.type == 'ARMATURE' and obj.type == 'ARMATURE':
            obj.select_set(True)

    bpy.context.view_layer.objects.active = target_obj
    target_obj.select_set(True)

    bpy.ops.object.join()

    target_obj.data.name = target_obj.name

    print_enhanced(f"{target_obj.name}", label="JOINED OBJECT", label_color="green")
    return target_obj


def pack_textures():
    print_enhanced(f"pack_textures", label="INFO", label_color="yellow")
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            print_enhanced(f"{image.name}", label="PACKING IMAGE", label_color="green")
            image.pack()


# HERE: it looks like the only purpose of this in the code is to have an empty named mid that could maybe used later on some other script?
def create_mid_point(name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    obj = bpy.context.object
    if obj is not None:
        obj.name = name
        print_enhanced("Middle Point Created", label="INFO", label_color="yellow")
        return obj
    return None


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
    scene.render.resolution_x = x
    scene.render.resolution_y = y


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


def import_usda_model(path, scan_ID, import_path):
    print_enhanced(f"Attempting to import USD model", label="INFO", label_color="yellow")

    if not file_exists(import_path):
        print_enhanced(f"import_usda_model failed | import_path: {import_path} doesn't exists", text_color="red", label="ERROR", label_color="red")
        return None

    # NOTE: Added some arguments to avoid importing materials and textures
    bpy.ops.wm.usd_import(filepath=import_path, import_materials=False, import_usd_preview=False, import_textures_mode='IMPORT_NONE')

    geo_list = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    if not geo_list:
        print_enhanced("import_usda_model: No mesh objects found after USD import", text_color="red", label="ERROR", label_color="red")
        return None

    mesh_obj = geo_list[0]
    mesh_obj.name = 'g0'

    # deselect all object, select 'g0' and make it the active object
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # clear 'g0' parent and apply its transforms
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    apply_transform(mesh_obj)

    # save the file for runShot script
    savepath = os.path.join(path ,str(scan_ID),"photogrammetry",str(scan_ID) + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=savepath)

    print_enhanced(f"Got 'g0' object from 'Geom' object", label="USD IMPORT", label_color="green")
    return mesh_obj


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


def separate_object_loose_parts(obj):
    if obj is None:
        print_enhanced("separate_object_loose_parts failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"separate_object_loose_parts | obj: {obj.name}", label="INFO", label_color="yellow")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')


def sort_by_vertex_count(obj):
    return len(obj.data.vertices)

def remove_objects_with_less_vertices(obj_list, remaining_obj_name=None):
    if not obj_list:
        print_enhanced("remove_objects_with_less_vertices failed | obj_list is Empty", text_color="red", label="ERROR", label_color="red")
        pass

    print_enhanced(f"remove_objects_with_less_vertices | obj_list: {obj_list}", label="INFO", label_color="yellow")

    parts = obj_list

    # sort by number of verts (last has most)
    parts.sort(key=sort_by_vertex_count)

    # pop off the last part
    highest_vertices_part = parts.pop()

    for part in parts:
        print_enhanced(f"Removing obj '{part.name}' vertices: {len(part.data.vertices)}", label="LOW VERTICES PART", label_color="magenta")
        print(part.name, len(part.data.vertices))

    print_enhanced(f"obj: {highest_vertices_part.name} | vertices: {len(highest_vertices_part.data.vertices)}", label="HIGH VERTICES PART", label_color="green")

    # remove the rest
    if len(parts) > 0:
        for obj in parts:
            bpy.data.objects.remove(obj)

    if remaining_obj_name:
        print_enhanced(f"obj '{highest_vertices_part.name}' to '{remaining_obj_name}'", label="RENAMING", label_color="green")
        highest_vertices_part.name = remaining_obj_name

    return highest_vertices_part


def clean_up_object_loose_parts(obj):
    # CLEAN UP DETRITUS - THIS CLEANS UP LOOSE BITS OF THE MESH
    print_enhanced(f"clean_up_object_loose_parts | obj: {obj.name}", label="INFO", label_color="yellow")

    separate_object_loose_parts(obj)

    parts = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    remaining_obj = remove_objects_with_less_vertices(parts, remaining_obj_name=obj.name)

    return remaining_obj
            
def select_feet(target):
    for v in bpy.data.objects[target].data.vertices:
        if v.co[2] < 0.03:
            v.select = True
    selectedVerts = [v for v in bpy.data.objects['g0'].data.vertices if v.select]


def set_object_origin_to_lowest_vertex(obj, offset_z, center_to_median=False):
    if obj is None:
        print_enhanced("set_object_origin_to_lowest_vertex failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"set_object_origin_to_lowest_vertex | obj: {obj.name} | offset_z: {offset_z}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Get the z-coordinates of the vertices
    z_coords = [vert.co[2] for vert in obj.data.vertices] # Removed if vert.co[2], we shouldn't need it since we're trying to the lowest vertices
    if not z_coords:
        print_enhanced("set_object_origin_to_lowest_vertex failed | z_coords is None", text_color="red", label="ERROR", label_color="red")
        return

    # Get the lowest vertex
    lowest_z = min(z_coords, default=None)

    cursor_location = (0, 0, lowest_z + offset_z)
    if center_to_median:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        cursor_location = (obj.location[0], obj.location[1], lowest_z + offset_z)

    # Set the cursor location to the lowest vertex plus the padding
    bpy.context.scene.cursor.location = cursor_location


    # Set the origin of the object to the cursor location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    print_enhanced(f"set to lowest_z: {lowest_z}", label=f"'{obj.name}' ORIGIN", label_color='green')

    # Move object to the world origin
    obj.location = (0, 0, 0)

    print_enhanced(f"set to (0, 0, 0)", label=f"'{obj.name}' LOCATION", label_color='green')


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


def recalculate_object_normals(obj, inside=False):
    if obj is None:
        print_enhanced("recalculate_object_normals failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"recalculate_object_normals | obj: {obj.name} | inside: {inside}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.normals_make_consistent(inside=inside)

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def fix_mesh_outside_normals(obj):
    """Hacky way to fix a mesh outside normals using an applied Solidify modifier and the shell output vertex group to delete the internal faces."""

    print_enhanced(f"fix_mesh_outside_normals | obj: {obj.name}", label="INFO", label_color="yellow")

    obj_copy = duplicate_object(obj)

    solidify_modifier, shell_vertex_group_name = add_solidify_modifier(obj_copy, thickness=0.01)

    apply_all_modifier(obj)

    if shell_vertex_group_name != "":
        select_vertex_group_vertices(obj, shell_vertex_group_name, delete_selected_faces=True, invert_selection=False)


def add_floor_v2(obj, floor_dimensions, floor_height, padding):
    if obj is None:
        print_enhanced("add_floor failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"add_floor | obj: {obj.name} | floor_height: {floor_height} | padding: {padding}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Set the origin of the mesh_obj to the lowest vertex + padding
    set_object_origin_to_lowest_vertex(obj, padding)

    # Create cube in edit mode to use as feet boolean mesh
    cube_scale = (floor_dimensions[0] / 2, floor_dimensions[1] / 2, floor_dimensions[2] / 2)
    cube_location = (0, 0, -cube_scale[2] + floor_height)

    create_cube_in_editmode(obj, location=cube_location, scale=cube_scale)


def bisect_mesh(obj, plane_point_vector, plane_normal_vector, clear_outer=False, clear_inner=False, fill_holes=False):
    """ When this ends, the context mode should be OBJECT and the slice of vertices should be selected"""

    if obj is None:
        print_enhanced("bisect_mesh failed | scan_obj = None", text_color="red", label="ERROR", label_color="red")
        return

    if not plane_point_vector or not plane_normal_vector:
        print_enhanced(f"bisect_mesh failed | plane_point_vector: {plane_point_vector} | plane_normal_vector: {plane_normal_vector}", text_color="red", label="ERROR", label_color="red")
        return

    # check if there is 

    print_enhanced(f"bisect_mesh obj= {obj.name} | plane_point_vector: {plane_point_vector} | plane_normal_vector: {plane_normal_vector}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    obj_data = obj.data

    # Deselect mesh in EDIT mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    # Back to OBJECT mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a bmesh object and load the cube mesh data into it
    bm = bmesh.new()
    bm.from_mesh(obj_data)

    # Define bisect plane - point and normal vector
    plane_point = plane_point_vector  # A point on the plane
    plane_normal = plane_normal_vector  # The plane's normal

    # Perform the bisection
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=plane_point, plane_no=plane_normal, clear_outer=clear_outer, clear_inner=clear_inner)

    bisect_verts = [v for v in result['geom_cut'] if isinstance(v, bmesh.types.BMVert)]

    if bisect_verts:
        # Select the vertices
        for vertex in bisect_verts:
            vertex.select = True

    # Update the mesh with the new data
    bm.to_mesh(obj_data)
    bm.free()

    if fill_holes:
        # check if there are selected vertices
        if not any(vertex.select for vertex in obj_data.vertices):
            print_enhanced("No vertices selected after bisecting, filling holes skipped.", text_color="yellow", label="WARNING", label_color="yellow")
            return
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.fill()

        bpy.ops.object.mode_set(mode='OBJECT')


def extract_floor(scan_obj, extract_height=0.011):
    if scan_obj is None:
        print_enhanced("extract_floor failed | scan_obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"extract_floor | extract_height: {extract_height}", label="INFO", label_color="yellow")

    bisect_point = Vector((0, 0, extract_height))
    bisect_normal = Vector((0, 0, 1))
    bisect_mesh(scan_obj, bisect_point, bisect_normal, clear_inner=True, fill_holes=True)


def reset_floor(obj, offset_z):
    if obj is None:
        print_enhanced("reset_floor failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"reset_floor | obj: {obj.name} | offset_z: {offset_z}", label="INFO", label_color="yellow")

    # STAGE 2 : Get Bottom Plane
    set_object_origin_to_lowest_vertex(obj, offset_z, center_to_median=True)

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(False)
    bpy.ops.object.mode_set(mode = 'OBJECT')


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


def separate_lower_legs(scan_obj_copy):
    if scan_obj_copy is None or scan_obj_copy.type != 'MESH':
        print_enhanced("separate_lower_legs failed | obj = None or obj.type != 'MESH'", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"separate_lower_legs | obj: {scan_obj_copy.name}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    scan_obj_copy.select_set(True)
    bpy.context.view_layer.objects.active = scan_obj_copy

    # Define the height threshold for selecting vertices
    height_threshold = 0.16

    # If it's a small person, lower the threshold to avoid cutting the body instead
    if scan_obj_copy.dimensions.z < 1.0:
        height_threshold = 0.06

    bisect_point = Vector((0, 0, height_threshold))
    bisect_normal = Vector((0, 0, 1))

    bisect_mesh(scan_obj_copy, bisect_point, bisect_normal, clear_outer=True)
    remove_doubles_bmesh(scan_obj_copy, merge_distance=0.005)
    remove_loose_geometry(scan_obj_copy, remove_linked_faces=True, max_linked_faces=200)

    bpy.ops.mesh.separate(type='LOOSE')

    if bpy.context.selected_objects:
        for i, leg in enumerate(bpy.context.selected_objects):
            leg.name = f"leg{i}"

    legs = [obj for obj in bpy.context.scene.objects if "leg" in obj.name]

    return legs


def find_farthest_vertex(vertex_reference, vertices):
    if not vertex_reference or not vertices:
        print_enhanced("find_farthest_vertex failed | not vertex_reference or not vertices", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"find_farthest_vertex | vertex_reference: {vertex_reference} | vertices: {len(vertices)}", label="INFO", label_color="yellow")

    # Initialize variables
    farthest_vertex = None
    max_distance = 0.0

    # Iterate over all vertices in the bmesh
    for vertex in vertices:
        distance = math.dist(vertex_reference.co, vertex.co)
        if distance > max_distance:
            max_distance = distance
            farthest_vertex = vertex

    return farthest_vertex

def separate_foot_tip_and_ankle_vertices(obj):
    if obj is None or obj.type != 'MESH':
        print_enhanced("separate_foot_tip_and_ankle_vertices failed | obj = None or obj.type != 'MESH'", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"separate_foot_tip_and_ankle_vertices | obj: {obj.name}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    obj_data = obj.data

    # Deselect mesh in EDIT mode
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    # Back to OBJECT mode
    bpy.ops.object.mode_set(mode='OBJECT')

    ankle_threshold = 0.07
    foot_threshold = 0.01

    if obj.dimensions.z < 0.14:
        ankle_threshold = 0.04 # to make sure it grabs the ankles when it's a small child

    print_enhanced(f"{ankle_threshold}", label="ANKLE THRESHOLD", label_color="green")
    print_enhanced(f"{foot_threshold}", label="FOOT THRESHOLD", label_color="green")

    ankle_vertices = [v for v in obj_data.vertices if v.co.z > ankle_threshold and v.co.z < ankle_threshold + 0.02]
    foot_vertices = [v for v in obj_data.vertices if v.co.z < foot_threshold]

    ankle_and_foot_vertices = ankle_vertices + foot_vertices

    if not ankle_and_foot_vertices:
        print_enhanced("No ankle_and_foot_vertices found", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"Selecting vertices", label="INFO", label_color="yellow")

    for vertex in ankle_and_foot_vertices:
        vertex.select = True

    print_enhanced(f"Inverting selection and deleting new selection", label="INFO", label_color="yellow")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    top_vertices = [v for v in obj_data.vertices if v.co.z > foot_threshold]

    if not top_vertices:
        print_enhanced("No top_vertices found", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"Selecting and merging top vertices", label="INFO", label_color="yellow")
    for vertex in top_vertices:
        vertex.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.merge(type='CENTER')

    # Back to OBJECT mode to find the ankle and foot tip vertices
    bpy.ops.object.mode_set(mode='OBJECT')

    ankle_and_foot_tip_vertices = [v for v in obj_data.vertices if v.co.z > foot_threshold]
    
    if not ankle_and_foot_tip_vertices:
        return
        
    ankle_vertex = ankle_and_foot_tip_vertices[0]
    foot_tip_vertex = find_farthest_vertex(ankle_vertex, obj_data.vertices)

    if foot_tip_vertex is None:
        return

    ankle_and_foot_tip_vertices.append(foot_tip_vertex)

    for vertex in ankle_and_foot_tip_vertices:
        vertex.select = True

    bpy.ops.object.mode_set(mode='EDIT')  
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')

    print_enhanced(f"Found ankle vertex and foot tip vertex, removed the rest", label="INFO", label_color="yellow")


def prepare_for_orientation(scan_obj):
    """
    return: [0] ankle_vertices, [1] foot_vertices, [2] lower_legs_vertices_obj
    """
    print_enhanced("Start", label="Prepare for Orientation", label_color="cyan")

    if scan_obj is None:
        print_enhanced("FAILED | obj = None", text_color="red", label="Prepare for Orientation", label_color="cyan")
        return
    print_enhanced(f"prepare_for_orientation | obj: {scan_obj.name}", label="INFO", label_color="yellow")

    scan_obj_copy = duplicate_object(scan_obj)

    lower_legs = separate_lower_legs(scan_obj_copy)

    if lower_legs:
        for leg in lower_legs:
            separate_foot_tip_and_ankle_vertices(leg)

    lower_legs_vertices_obj = join_objects(lower_legs[0], lower_legs)

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    lower_legs_vertices_obj_data = lower_legs_vertices_obj.data

    ankle_vertices = [v for v in lower_legs_vertices_obj_data.vertices if v.co.z > 0.03]
    feet_vertices = [v for v in lower_legs_vertices_obj_data.vertices if v.co.z < 0.03]

    print_enhanced("End", label="Prepare for Orientation", label_color="cyan", suffix="\n")

    return ankle_vertices, feet_vertices, lower_legs_vertices_obj


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


def calculate_direction_vector(base_location, target_location):
    if not base_location or not target_location:
        print_enhanced("calculate_direction_vector failed | missing locations", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"calculate_direction_vector | base_location: {base_location} | target_location: {target_location}", label="INFO", label_color="yellow")

    # Calculate the direction vector from base_location to target_location
    direction = Vector(target_location) - Vector(base_location)

    direction_normalized = direction.normalized()

    print_enhanced(f"{direction_normalized}", label="NORMALIZED DIRECTION", label_color="green")
    
    return direction_normalized


def calculate_rotation_quaternion(direction_vector, axis=(1, 0, 0)):
    if not direction_vector:
        print_enhanced("calculate_rotation_quaternion failed | missing direction_vector", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"calculate_rotation_quaternion | direction_vector: {direction_vector} | axis: {axis}", label="INFO", label_color="yellow")

    # Define the target vector along the specified axis
    target_vector = Vector(axis)

    # Calculate the rotation quaternion
    rotation_quaternion = direction_vector.rotation_difference(target_vector)

    print_enhanced(f"{rotation_quaternion}", label="QUATERNION", label_color="green")

    return rotation_quaternion


def rotate_object_to_quaternion(obj, rotation_quaternion):
    if obj is None:
        print_enhanced("rotate_object_to_rotation_quaternion failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return
    print_enhanced(f"rotate_object_to_rotation_quaternion | obj: {obj.name} | rotation_quaternion: {rotation_quaternion}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    if obj.rotation_mode == 'QUATERNION':
        obj.rotation_quaternion = rotation_quaternion
        return

    euler_rotation = rotation_quaternion.to_euler(obj.rotation_mode)
    obj.rotation_euler = euler_rotation

    print_enhanced(f"to {euler_rotation}", label=f"{obj.name} ROTATED", label_color="green")


def remove_object(obj):
    if obj is None:
        print_enhanced("remove_object failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    if not obj.name in bpy.data.objects:
        print_enhanced("remove_object failed | obj.name not in bpy.data.objects", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"remove_object | obj: {obj.name}", label="INFO", label_color="yellow")

    bpy.data.objects.remove(obj, do_unlink=True)


def calculate_angle_between_two_vectors(vector0=(1, 0, 0), vector1=(0, 1, 0)):
    """ Doesn't actually uses mathutils Vectors, it uses locations"""

    # Calculate the dot product
    dot_product = sum(a*b for a, b in zip(vector0, vector1))

    # Calculate the magnitudes of the vectors
    magnitude0 = math.sqrt(sum(a*a for a in vector0))
    magnitude1 = math.sqrt(sum(a*a for a in vector1))

    # Return the angle in degrees
    if magnitude0 == 0 or magnitude1 == 0:
        return 0

    return math.degrees(math.acos(dot_product / (magnitude0 * magnitude1)))


def calculate_dot_product(vector1, vector2):
    """
    - If it's positive, it means the vectors are pointing somewhat in the same direction.
    - If it's negative, they're pointing in somewhat opposite directions.
    - If it's zero, the vectors are perpendicular, meaning they meet at a right angle.
    """
    print_enhanced(f"calculate_dot_product | vector1: {vector1} | vector2: {vector2}", label="INFO", label_color="yellow")
    numpy_v1 = numpy.array(vector1)
    numpy_v2 = numpy.array(vector2)
    result = numpy.dot(numpy_v1, numpy_v2)

    print_enhanced(f"result: {result}", label="DOT PRODUCT", label_color="green")
    return result


def find_farthest_opposing_vertices(obj):
    """
    - The vertices coordinates are in local space.
    - Use obj.world_matrix @ vertex.co to get world space coordinates
    """

    # Get vertices
    vertices = obj.data.vertices

    if not vertices:
        print_enhanced("find_farthest_opposing_vertices failed | No vertices found", text_color="red", label="ERROR", label_color="red")
        return None

    # Get vertices coordinates as a 2D numpy array of floats
    co = numpy.array([v.co[:] for v in vertices])  # Extract coordinates as tuples

    # Calculate the norms (distances to origin)
    norms = numpy.linalg.norm(co, axis=1)

    # Find the index of the vertex with the largest norm
    idx_max = numpy.argmax(norms)

    # This is the vertex that is farthest from the origin
    vertex_max = vertices[idx_max]

    # Now find the vertex farthest from vertex_max, but in the opposite direction.
    # We do this by finding the vertex that, when added to vertex_max, gives the smallest norm.
    opposite_co = co + numpy.array(vertex_max.co)  # Convert vertex_max.co to numpy array
    opposite_norms = numpy.linalg.norm(opposite_co, axis=1)
    idx_min = numpy.argmin(opposite_norms)

    # This is the vertex that is farthest from the origin in the opposite direction
    vertex_min = vertices[idx_min]

    return vertex_max, vertex_min


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


def re_orient_v1_using_two_legs(scan_obj, leg_obj, lower_legs_vertices):
    print_enhanced("Start", label="Re-orient Using Two Legs", label_color="cyan")
    if scan_obj is None:
        print_enhanced("FAILED | scan_obj = None", text_color="red", label="Re-orient Using Two Legs", label_color="cyan", suffix="\n")
        return "FAILED"

    if leg_obj is None:
        print_enhanced("FAILED | leg_obj = None", text_color="red", label="Re-orient Using Two Legs", label_color="cyan", suffix="\n")
        return "FAILED"

    print_enhanced(f"scan_obj: {scan_obj.name} | lower_legs_vertices: {lower_legs_vertices}", label="INFO", label_color="yellow")

    ankle_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in lower_legs_vertices[0]]

    if len(ankle_vertices_locations) < 2:
        print_enhanced(f"End WARNING | ONLY ONE LEG: {ankle_vertices_locations}", text_color="yellow", label="Re-orient Using Two Legs", label_color="cyan", suffix="\n")
        return "ONLY_ONE"

    if len(ankle_vertices_locations) > 2:
        print_enhanced(f"End WARNING | MORE THAN TWO LEGS: {ankle_vertices_locations}", text_color="yellow", label="Re-orient Using Two Legs", label_color="cyan", suffix="\n")
        return "MORE_THAN_TWO"

    direction_vector = calculate_direction_vector(base_location=ankle_vertices_locations[0], target_location=ankle_vertices_locations[1])
    rotation_quaternion = calculate_rotation_quaternion(direction_vector, axis=(-1.0, 0, 0))

    rotate_object_to_quaternion(scan_obj, rotation_quaternion)
    rotate_object_to_quaternion(leg_obj, rotation_quaternion)

    set_object_origin_to_lowest_vertex(scan_obj, offset_z=0.0, center_to_median=True)

    apply_transform(scan_obj)
    apply_transform(leg_obj)

    print_enhanced("End: SUCCESS", label="Re-orient Using Two Legs", label_color="cyan", suffix="\n")
    return "SUCCESS"


def re_orient_v2_using_shoulders(scan_obj, leg_obj):
    print_enhanced("Start", label="Re-orient Using Shoulders", label_color="cyan")
    if scan_obj is None:
        print_enhanced("FAILED | scan_obj = None", text_color="red", label="Re-orient Using Shoulders", label_color="cyan")
        return

    if leg_obj is None:
        print_enhanced("WARNING leg_obj = None", text_color="yellow", label="Re-orient Using Shoulders", label_color="cyan")

    print_enhanced(f"scan_obj: {scan_obj.name}", label="INFO", label_color="yellow")

    shoulders_obj = duplicate_object(scan_obj)
    shoulders_obj.name = "shoulders"

    shoulders_slice_height = (shoulders_obj.dimensions.z / 5) * 4

    if shoulders_obj.dimensions.z < 1.5:
        shoulders_slice_height = ((shoulders_obj.dimensions.z / 4) * 3 ) - 0.03 # eyeballed value that seems to work for smaller people

    bisect_point = Vector((0, 0, shoulders_slice_height))
    bisect_normal = Vector((0, 0, 1))

    bisect_mesh(shoulders_obj, bisect_point, bisect_normal, clear_inner=True, clear_outer=True)

    remove_doubles_bmesh(scan_obj, merge_distance=0.011)

    farthest_opposing_vertices = find_farthest_opposing_vertices(shoulders_obj)

    if farthest_opposing_vertices is None:
        print_enhanced("FAILED", text_color="red", label="Re-orient Using Shoulders", label_color="cyan", suffix="\n")
        return False

    vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in farthest_opposing_vertices]

    if len(vertices_locations) < 2:
        print_enhanced(f"FAILED | less than 2 vertices_locations: {vertices_locations}", text_color="red", label="Re-orient Using Shoulders", label_color="cyan")
        return False

    direction_vector = calculate_direction_vector(base_location=vertices_locations[0], target_location=vertices_locations[1])
    rotation_quaternion = calculate_rotation_quaternion(direction_vector, axis=(-1.0, 0, 0))

    rotate_object_to_quaternion(scan_obj, rotation_quaternion)
    rotate_object_to_quaternion(shoulders_obj, rotation_quaternion)
    rotate_object_to_quaternion(leg_obj, rotation_quaternion)

    set_object_origin_to_lowest_vertex(scan_obj, offset_z=0.0, center_to_median=True)

    apply_transform(scan_obj)
    apply_transform(shoulders_obj)
    apply_transform(leg_obj)

    print_enhanced("End WARNING: Worked but may be facing backwards", text_color="yellow", label="Re-orient Using Shoulders", label_color="cyan")
    return True


def re_orient_v3_using_more_than_two_legs(scan_obj, leg_obj):
    if scan_obj is None:
        print_enhanced("re_orient_v3_using_more_than_two_legs failed | scan_obj = None", text_color="red", label="ERROR", label_color="red")
        return

    if leg_obj is None:
        print_enhanced("leg_obj = None", text_color="yellow", label="WARNING", label_color="red")

    print_enhanced(f"re_orient_v3_using_more_than_two_legs | scan_obj: {scan_obj.name}", label="INFO", label_color="yellow")

    leg_vertices = leg_obj.data.vertices

    ankle_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in leg_vertices if vertex.co.z > 0.03]
    foot_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in leg_vertices if vertex.co.z < 0.03]

    ankles_mid_location = find_middle_location(ankle_vertices_locations)
    feet_mid_location = find_middle_location(foot_vertices_locations)

    print_enhanced(f"{ankles_mid_location}", label="ANKLES MID LOCATION", label_color="green")
    print_enhanced(f"{feet_mid_location}", label="FEET MID LOCATION", label_color="green")

    direction_vector = calculate_direction_vector(base_location=ankles_mid_location, target_location=feet_mid_location)
    rotation_quaternion = calculate_rotation_quaternion(direction_vector, axis=(0, -1.0, 0))

    if len(ankle_vertices_locations) < 3:
        print_enhanced(f"re_orient_v3_using_more_than_two_legs failed | less than 3 ankle_vertices_locations: {ankle_vertices_locations}", text_color="yellow", label="WARNING", label_color="yellow")
        return False

    rotate_object_to_quaternion(scan_obj, rotation_quaternion)
    rotate_object_to_quaternion(leg_obj, rotation_quaternion)

    set_object_origin_to_lowest_vertex(scan_obj, offset_z=0.0, center_to_median=True)

    apply_transform(scan_obj)
    apply_transform(leg_obj)

    return True


def check_orientation_v1_using_a_single_leg(scan_obj, leg_obj):
    print_enhanced("Start", Label="Check Orientation Using Single Leg", label_color="cyan")
    if scan_obj is None:
        print_enhanced("FAILED | scan_obj = None", text_color="red", label="Check Orientation Using Single Leg", label_color="cyan")
        return False

    if leg_obj is None:
        print_enhanced("FAILED | leg_obj = None", text_color="red", label="Check Orientation Using Single Leg", label_color="cyan")
        return False

    print_enhanced(f"scan_obj: {scan_obj.name} | leg_obj: {leg_obj.name}", label="INFO", label_color="yellow")

    leg_obj_data = leg_obj.data
    ankle_vertices = [v for v in leg_obj_data.vertices if v.co.z > 0.03]

    if not ankle_vertices or len(ankle_vertices) > 1:
        print_enhanced("FAILED | not ankle_vertices or len(ankle_vertices) > 1", text_color="red", label="Check Orientation Using Single Leg", label_color="cyan")
        return False

    ankle_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in ankle_vertices]
    ankle_mid_location = find_middle_location(ankle_vertices_locations)

    feet_vertices = [v for v in leg_obj_data.vertices if v.co.z < 0.03]
    feet_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in feet_vertices]
    feet_mid_location = find_middle_location(feet_vertices_locations)

    front_axis = (0, -1, 0)
    feet_direction = calculate_direction_vector(ankle_mid_location, feet_mid_location)
    dot_product = calculate_dot_product(front_axis, feet_direction)

    # check if the feet tip Y axis value is higher than 0, meaning that is back facing and should be rotated by 180
    if dot_product < 0:
        print_enhanced(f"Fixing: Rotating 180°", text_color="green", label="FACING BACK", label_color="red")
        scan_obj.rotation_euler[2] = math.radians(180)

    apply_transform(scan_obj)
    print_enhanced("End", Label="Check Orientation Using Single Leg", label_color="cyan")

    return True


def check_orientation_v2_using_more_than_one_leg(scan_obj, leg_obj):
    if scan_obj is None:
        print_enhanced("check_front_back_facing_using_two_legs failed | scan_obj = None", text_color="red", label="ERROR", label_color="red")
        return False

    if leg_obj is None:
        print_enhanced("check_front_back_facing_using_two_legs failed | leg_obj = None", text_color="red", label="ERROR", label_color="red")
        return False

    print_enhanced(f"check_front_back_facing_using_two_legs | scan_obj: {scan_obj.name} | leg_obj: {leg_obj.name}", label="INFO", label_color="yellow")

    leg_obj_data = leg_obj.data
    feet_vertices = [v for v in leg_obj_data.vertices if v.co.z < 0.03]
    feet_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in feet_vertices]

    ankle_vertices = [v for v in leg_obj_data.vertices if v.co.z > 0.03]
    ankle_vertices_locations = [(vertex.co.x, vertex.co.y, 0.0) for vertex in ankle_vertices]

    feet_mid_location = find_middle_location(feet_vertices_locations)
    ankle_mid_location = find_middle_location(ankle_vertices_locations)

    front_axis = (0, -1, 0)
    feet_direction = calculate_direction_vector(ankle_mid_location, feet_mid_location)
    dot_product = calculate_dot_product(front_axis, feet_direction)

    # check if the feet tip Y axis value is higher than 0, meaning that is back facing and should be rotated by 180
    if dot_product < 0:
        print_enhanced(f"Fixing: Rotating 180°", text_color="green", label="FACING BACK", label_color="red")
        scan_obj.rotation_euler[2] = math.radians(180)

    apply_transform(scan_obj)

    return True


def move_feet_vertices_to_zero(obj, vertices_min_height):
    if obj is None:
        print_enhanced("move_feet_vertices_to_zero failed | obj = None", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"move_feet_vertices_to_zero  | obj: {obj.name} | vertices_min_height: {vertices_min_height}", label="INFO", label_color="yellow")

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Create a BMesh object from the mesh data
    b_mesh = bmesh.new()
    b_mesh.from_mesh(obj.data)

    # Ensure the vertex lookup table is up-to-date
    b_mesh.verts.ensure_lookup_table()

    # Move the selected vertices to 0
    for v in b_mesh.verts:
        if v.co[2] < vertices_min_height + 0.00001:
            v.co[2] = 0.0

    # Update the mesh data with the modified BMesh
    b_mesh.to_mesh(obj.data)
    obj.data.update()


def move_object_to_collection(obj, collection_name):
    print_enhanced(f"move_to_collection | collection_name: {collection_name}", label="INFO", label_color="yellow")

    # Get the collection to move the object to
    collection = bpy.data.collections.get(collection_name)

    # If the collection doesn't exist, create it and link it to the scene
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        print_enhanced(f"'{collection_name}' created", label=f"COLLECTION", label_color="green")

    # Move the object to the collection
    obj_collection = obj.users_collection[0]
    obj_collection.objects.unlink(obj)
    collection.objects.link(obj)
    print_enhanced(f"Linked to collection: {collection_name}", label=f"'{obj.name}' OBJECT", label_color="green")


def save_file():
    print_enhanced(f"Attempting to Save the File", label="INFO", label_color="yellow")
    try:
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print_enhanced(f"Save File failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


def render(obj, camera_obj, output_path):
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


def stop_script():
    save_file()
    print_enhanced("Break Point", text_color="red", label="STOP", label_color="red")
    raise SystemExit()


def bmesh_select_faces_by_vector_direction(vector_direction, angle_threshold, invert_selection=False):
    # Ensure we are in object mod
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get the active object
    mesh = bpy.context.active_object

    # Get the mesh data
    mesh_data = mesh.data

    # Create a bmesh object and load the mesh data
    bm = bmesh.new()
    bm.from_mesh(mesh_data)

    visible_faces = []
    non_visible_faces = []

    # Check visibility for each face
    for face in bm.faces:
        face.select = False  # Initially deselect all faces
        face_normal = mesh.matrix_world.to_3x3() @ face.normal  # transform the normal to world space

        # Check if the angle between the camera-mesh direction and the face normal is within the threshold
        angle = math.degrees(face_normal.angle(vector_direction))
        if angle < angle_threshold:
            non_visible_faces.append(face)
        else:
            visible_faces.append(face)

    # Select visible faces
    if not invert_selection:
        for face in visible_faces:
            face.select = True
    else:
        for face in non_visible_faces:
            face.select = True

    # Flush selection to propagate face selections to vertices/edges
    bm.select_flush(False)

    # Update the mesh to show the selection
    bm.to_mesh(mesh_data)
    bm.free()

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')


def mesh_select_more(repeat=2):
    """
    Selects more faces in edit mode.
    :param amount: Number of times to select more faces.
    """
    if bpy.context.mode != 'EDIT_MESH':
        print_enhanced("mesh_select_more failed | not in EDIT_MESH mode", text_color="red", label="ERROR", label_color="red")
        return

    print_enhanced(f"mesh_select_more | amount: {repeat}", label="INFO", label_color="yellow")

    for _ in range(repeat):
        bpy.ops.mesh.select_more()


def mesh_get_selected_vertices(obj=None):
    """
    Get the selected vertices of the mesh object.
    :param obj: The mesh object to get the selected vertices from. If None, uses the active object.
    :return: A list of selected vertices' coordinates.
    """
    if obj is None:
        obj = bpy.context.active_object

    if obj is None or obj.type != 'MESH':
        print_enhanced("mesh_get_selected_vertices failed | invalid object", text_color="red", label="ERROR", label_color="red")
        return []

    selected_vertices = [v for v in obj.data.vertices if v.select]

    return selected_vertices


def get_bounding_box(obj, bboxOffset=0.4):
    """
    Get the bounding box of the object in world space coordinates
    :param obj: The object to get the bounding box for
    :param bboxOffset: The offset to apply to the bounding box
    """
    if obj is None:
        return

    # making we're in OBJECT mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Deselect all vertices
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='SELECT')

    # Get all 8 corners of the bounding box in local space and transform to world space
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Find min/max in world space
    min_x = min(corner.x for corner in bbox_corners)
    max_x = max(corner.x for corner in bbox_corners)
    min_y = min(corner.y for corner in bbox_corners)
    max_y = max(corner.y for corner in bbox_corners)
    min_z = min(corner.z for corner in bbox_corners)
    max_z = max(corner.z for corner in bbox_corners)

    # Apply offset to grow the bounding box
    min_x = round(min_x - bboxOffset, 2)
    max_x = round(max_x + bboxOffset, 2)
    min_y = round(min_y - bboxOffset, 2)
    max_y = round(max_y + bboxOffset, 2)
    min_z = round(min_z - bboxOffset, 2)
    max_z = round(max_z + bboxOffset, 2)

    return (min_x, max_x, min_y, max_y, min_z, max_z)


def deselect_vertices_inside_xy_bounds(obj=None, min_x=None, max_x=None, min_y=None, max_y=None):
    """
    Deselect vertices of a mesh inside the specified bounding box in world space.

    Args:
        obj (bpy.types.Object, optional): Mesh object to process. Defaults to active object.
        min_x, max_x (float, optional): X-axis bounds in world space.
        min_y, max_y (float, optional): Y-axis bounds in world space.
        min_z, max_z (float, optional): Z-axis bounds in world space.
    """
    # Use active object if none provided
    if obj is None:
        obj = bpy.context.edit_object
    if obj is None or obj.type != 'MESH':
        print_enhanced("deselect_vertices_inside_bounds failed | invalid object", text_color="red", label="ERROR", label_color="red")
        return

    # Ensure Edit Mode
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')

    # Debug: Print the provided bounds
    print_enhanced(f"deselect_vertices_inside_bounds: Bounds provided: min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}", label="DEBUG", label_color="cyan")

    # Get mesh and create bmesh
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    # Count selected vertices before modification
    initial_selected = [v for v in bm.verts if v.select]
    print_enhanced(f"Initial selected vertices count: {len(initial_selected)}", label="DEBUG", label_color="cyan")

    # Get world matrix for transforming vertex coordinates
    world_matrix = obj.matrix_world

    deselected_count = 0
    # Deselect vertices inside bounds
    for vert in bm.verts:
        if vert.select:
            # Transform vertex coordinates to world space
            world_co = world_matrix @ vert.co
            x, y, z = world_co

            # Check if vertex is inside all specified bounds
            inside_bounds = (
                (min_x is None or x >= min_x) and
                (max_x is None or x <= max_x) and
                (min_y is None or y >= min_y) and
                (max_y is None or y <= max_y)
            )

            # Deselect if inside bounds
            if inside_bounds:
                vert.select = False
                deselected_count += 1

    # Flush selection to ensure consistency across vertices, edges, and faces
    bm.select_flush(False)

    # Update mesh
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)

    # Count selected vertices after modification
    final_selected = [v for v in bm.verts if v.select]
    print_enhanced(f"Final selected vertices count: {len(final_selected)} (Deselected {deselected_count})", label="DEBUG", label_color="cyan")


def mesh_select_vertex_with_max_z_from_selection(obj=None):
    """
    Find and select the vertex with the maximum Z-coordinate from the current selection in world space.
    Deselects all other vertices.

    Args:
        obj (bpy.types.Object, optional): Mesh object to process. Defaults to active object.
    """

    vertex_max_z = 0

    # Use active object if none provided
    if obj is None:
        obj = bpy.context.edit_object
    if obj is None or obj.type != 'MESH':
        print_enhanced("select_vertex_with_max_z failed | invalid object", text_color="red", label="ERROR", label_color="red")
        return vertex_max_z

    # Ensure Edit Mode
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')

    # Get mesh and create bmesh
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    # Count selected vertices before modification
    initial_selected = [v for v in bm.verts if v.select]
    print_enhanced(f"Initial selected vertices count: {len(initial_selected)}", label="DEBUG", label_color="cyan")

    if not initial_selected:
        print_enhanced("No vertices selected, cannot find max Z", text_color="yellow", label="WARNING", label_color="yellow")
        return vertex_max_z

    # Get world matrix for transforming vertex coordinates
    world_matrix = obj.matrix_world

    # Find vertex with maximum Z-coordinate
    max_z = float('-inf')
    max_z_vertex = None

    for vert in bm.verts:
        if vert.select:
            # Transform vertex coordinates to world space
            world_co = world_matrix @ vert.co
            z = world_co.z
            if z > max_z:
                max_z = z
                max_z_vertex = vert

    if max_z_vertex is None:
        print_enhanced("No valid vertex found with max Z", text_color="yellow", label="WARNING", label_color="yellow")
        return vertex_max_z

    # Deselect all vertices
    for vert in bm.verts:
        vert.select = False

    # Select only the vertex with max Z
    max_z_vertex.select = True

    # Flush selection to ensure consistency across vertices, edges, and faces
    bm.select_flush(False)

    # Update mesh
    bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)

    vertex_max_z = max_z_vertex.co.z

    return vertex_max_z

def initialize_clean_scene():
    print_decorated("Starting with a clean scene")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bpy.context.preferences.filepaths.save_version = 0
    bpy.context.preferences.filepaths.use_auto_save_temporary_files = False
    bpy.context.preferences.filepaths.use_file_compression = True

    print_enhanced("Attempting to create World", label="INFO", label_color="yellow")
    try:
        bpy.ops.world.new()

        if not bpy.data.worlds:
            print_enhanced("World not found", label="ERROR", label_color="red")
            return None
        bpy.context.scene.world = bpy.data.worlds[0]
        print_enhanced("World created successfully", label="INFO", label_color="green")
    except Exception as e:
        print_enhanced(f"Failed to create World: {e}", text_color="red", label="ERROR", label_color="red")
        return None

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
def main():
    # HERE: COMMAND LINE ARGS
    print_decorated("Command line Arguments")

    ARGS = get_args()
    SCAN = str(ARGS.scan)
    PATH = str(ARGS.path)
    FEET_HEIGHT_OFFSET = float(ARGS.padding)
    FLOOR_EXTRACT_OFFSET = float(ARGS.floor_height)
    USE_CLEAN_START = int(ARGS.clean_start)
    ENVIRONMENT_MAP = str(ARGS.environment_map)
    USE_CLEANING_1 = int(ARGS.use_cleaning_1)
    USE_CLEANING_2 = int(ARGS.use_cleaning_2)
    USE_ORIENTATION = int(ARGS.use_orientation)
    OUTPUT_RESOLUTION = [int(res) for res in str(ARGS.output_resolution).split('_')]

    print_enhanced(SCAN, label="SCAN", label_color="cyan")
    print_enhanced(PATH, label="PATH", label_color="cyan")
    print_enhanced(FEET_HEIGHT_OFFSET, label="FEET_HEIGHT_OFFSET", label_color="cyan")
    print_enhanced(FLOOR_EXTRACT_OFFSET, label="FLOOR HEIGHT", label_color="cyan")
    print_enhanced(ENVIRONMENT_MAP, label="ENVIRONMENT MAP", label_color="cyan")
    print_enhanced(OUTPUT_RESOLUTION, label="OUTPUT RESOLUTION", label_color="cyan")

    # HERE: MAIN VARIABLES
    print_decorated("Main variables")

    texture_path = os.path.join(PATH, str(SCAN), "photogrammetry", "baked_mesh_tex0.png")
    material_name = "MAT"
    floor_dimensions = (11, 11, 8)
    extract_floor_threshold = 0.0001
    lower_threshold = 0.2
    import_usd_path = os.path.join(PATH ,str(SCAN),"photogrammetry","baked_mesh.usda")

    print_enhanced(texture_path, label="SCAN TEXTURE PATH", label_color="cyan")
    print_enhanced(material_name, label="MATERIAL NAME", label_color="cyan")
    print_enhanced(floor_dimensions, label="FLOOR DIMENSIONS", label_color="cyan")
    print_enhanced(extract_floor_threshold, label="EXTRACT FLOOR THRESHOLD", label_color="cyan")
    print_enhanced(lower_threshold, label="LOWER THRESHOLD", label_color="cyan")
    print_enhanced(import_usd_path, label="IMPORT USD PATH", label_color="cyan")

    # HERE: CLEAN START
    if USE_CLEAN_START == 1:
        initialize_clean_scene()

    # HERE: SCENE SETUP
    print_decorated("Importing and setting up the mesh")

    scan_obj = import_usda_model(PATH, SCAN, import_usd_path)

    if scan_obj is None:
        print_enhanced("CANCELLED", text_color="red", label="ERROR", label_color="red")

    SCAN_OBJ_MATERIAL = create_material(material_name, texture_path)
    add_material_to_object(scan_obj, SCAN_OBJ_MATERIAL)

    # HERE: CLEANING 1
    if USE_CLEANING_1 == 1:
        print_decorated("Cleaning 1")

        MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z = get_bounding_box(scan_obj, bboxOffset=0)
        BOUNDS_OFFSET = 0.20
        FEET_OFFSET = -0.02

        bmesh_select_faces_by_vector_direction(vector_direction=Vector((0,0,-1)), angle_threshold=175)
        mesh_select_more(repeat=2)
        deselect_vertices_inside_xy_bounds(scan_obj, min_x=MIN_X + BOUNDS_OFFSET, max_x=MAX_X - BOUNDS_OFFSET, min_y=MIN_Y + BOUNDS_OFFSET, max_y=MAX_Y - BOUNDS_OFFSET)

        MESH_FLOOR_HEIGHT = mesh_select_vertex_with_max_z_from_selection(scan_obj) + FLOOR_EXTRACT_OFFSET

        extract_floor(scan_obj, extract_height=MESH_FLOOR_HEIGHT)
        reset_floor(scan_obj, offset_z=FEET_OFFSET)
        move_feet_vertices_to_zero(scan_obj, -FEET_OFFSET)

        # cleans up and returns the highest vertices count object
        REMAINING_OBJ = clean_up_object_loose_parts(scan_obj)

        # updating the variable since g0 may be lost in the previous step
        scan_obj = REMAINING_OBJ

    # HERE: ORIENTATION
    if USE_ORIENTATION == 1:
        print_decorated("Orientation")

        lower_legs_data = prepare_for_orientation(scan_obj)
        leg_obj = lower_legs_data[2]

        re_orient_v1_result = re_orient_v1_using_two_legs(scan_obj, leg_obj, lower_legs_data)

        if re_orient_v1_result == "SUCCESS":
            check_orientation_v2_using_more_than_one_leg(scan_obj, leg_obj)

        if re_orient_v1_result == "ONLY_ONE":
            re_orient_v2_result = re_orient_v2_using_shoulders(scan_obj, leg_obj)
            if re_orient_v2_result:
                check_orientation_v1_using_a_single_leg(scan_obj, leg_obj)

        if re_orient_v1_result == "MORE_THAN_ONE":
            re_orient_v3_result = re_orient_v3_using_more_than_two_legs(scan_obj, leg_obj)
            if re_orient_v3_result:
                check_orientation_v2_using_more_than_one_leg(scan_obj, leg_obj)

    # HERE: CLEANING 2
    if USE_CLEANING_2 == 1:
        print_decorated("Cleaning 2")

        remove_loose_geometry(scan_obj, remove_linked_faces=True, max_linked_faces=200)
        close_mesh_holes(scan_obj)
        remove_doubles_bmesh(scan_obj)

    # HERE: ORGANIZING
    print_decorated("Organizing Scene")

    # Removing re_orient objects
    lower_legs_vertices = [obj for obj in bpy.context.scene.objects if "leg" in obj.name]
    shoulders_vertices = [obj for obj in bpy.context.scene.objects if "shoulders" in obj.name]

    for obj in lower_legs_vertices:
        remove_object(obj)

    for obj in shoulders_vertices:
        remove_object(obj)

    # Textures and Camera
    add_hdr_environment(image_path=ENVIRONMENT_MAP)
    pack_textures()
    # CAM_LOCATION = (0, -1.56, 0.8762)
    CAM_LOCATION = (0, -1, 1.1)
    CAM_ROTATION = (90, 0, 0)
    ORTHO_SCALE = 2.3
    camera = create_ortho_camera(location=CAM_LOCATION, rotation_in_degrees=CAM_ROTATION, ortho_scale=ORTHO_SCALE)

    # Moving objects to collections
    misc_objects = [obj for obj in bpy.context.scene.objects if scan_obj.name not in obj.name]
    for obj in misc_objects:
        move_object_to_collection(obj, collection_name="Collection")
    move_object_to_collection(scan_obj, collection_name="geo")

    # HERE: RENDERING AND SAVING
    print_decorated("Rendering and Saving")

    # Rendering
    set_scene_resolution(x=OUTPUT_RESOLUTION[0], y=OUTPUT_RESOLUTION[1])
    render_output_path = os.path.join(PATH, str(SCAN), "photogrammetry", f"{SCAN}.png")
    render(scan_obj, camera, render_output_path)
    save_file()

    return SCAN

if __name__ == '__main__': 
    IT = time.perf_counter()

    scan_ID = main()

    ET_S = time.perf_counter() - IT
    print_enhanced(f"Total Elapsed Time: {ET_S} sec", label=f"ID: {scan_ID} | CleanUp FINISHED", label_color="green")