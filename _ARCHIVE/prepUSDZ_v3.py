import os
import bpy
import math
import bmesh
import argparse
from mathutils import Vector
from typing import NamedTuple


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ prepUSDZ_v3 ▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 9.22.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


# This is the beginning of the preparation script for the USDZ file
# This script will be executed before the USDZ file is exported
# Need to add import of USDZ file and EXPORT of USDZ file
# Currently this script unparents the model, freezes transforms, and deletes the bottom and top vertices
# This script will import a USDZ file, delete the bottom and top vertices, get the bounding box of the person, and export a new USDZ file


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
    parser.add_argument('-l', '--use_locally', help="1: use command line arguments 0: use in grooveMeshCheck", default="0") 
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


def create_mid_point(name):
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    obj = bpy.context.object
    if obj is not None:
        obj.name = name
        print_enhanced("Middle Point Created", label="INFO", label_color="yellow")
        return obj
    return None


def file_exists(filepath):
    return os.path.isfile(filepath)


def import_usda_model(import_path):
    print_enhanced(f"Attempting to import USD model", label="INFO", label_color="yellow")

    if not file_exists(import_path):
        print_enhanced(f"import_usda_model failed | import_path: {import_path} doesn't exists", text_color="red", label="ERROR", label_color="red")
        return None
    
    # NOTE: Added some arguments to avoid importing materials and textures
    bpy.ops.wm.usd_import(filepath=import_path, import_materials=False, import_usd_preview=False, import_textures_mode='IMPORT_NONE')

    # get the mesh object
    mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

    mesh_obj = None
    if mesh_objs:
        mesh_obj = mesh_objs[0]

    # deselect all object, select mesh_obj and make it the active object
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # clear mesh_obj parent and apply its transforms
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    apply_transform(mesh_obj)

    print_enhanced(f"Got {mesh_obj.name} object from the scene objects", label="USD IMPORT", label_color="green")
    return mesh_obj


def move_object_to_collection(obj, collection_name):
    #print_enhanced(f"move_to_collection | collection_name: {collection_name}", label="INFO", label_color="yellow")

    # Get the collection to move the object to
    collection = bpy.data.collections.get(collection_name)
    
    # If the collection doesn't exist, create it and link it to the scene
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # if the object is not orphan, remove it from the collections
    if obj.users_collection:
        for user_collection in obj.users_collection:
            user_collection.objects.unlink(obj)

    # Move the object to the collection
    collection.objects.link(obj)


def create_empty_on_location (name='Empty', location=(0,0,0), radius=0.015, type='PLAIN_AXES', show_in_front=True, link_to_collection=""): 
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT') 

    bpy.ops.object.empty_add(radius=radius, type=type, location=location)
    obj = bpy.context.object
    bpy.context.view_layer.objects.active = obj
    obj.name = name
    obj.show_in_front = True

    if link_to_collection != "":
        move_object_to_collection(obj, collection_name=link_to_collection)

    return obj


def save_as(filepath):
    try:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
    except Exception as e:
        print(f"save_as failed | ERROR: {e}")


def mesh_delete_selection(obj, type='VERT'):
    if obj is None:
        return

    # making we're in OBJECT mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Delete selection
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.ops.mesh.delete(type=type)

    # back to OBJECT mode
    bpy.ops.object.mode_set(mode='OBJECT')


def separate_object_loose_parts(obj):
    if obj is None:
        return
    
    # making we're in OBJECT mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')


def select_highest_vertices(obj, threshold):
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
    bpy.ops.mesh.select_all(action='DESELECT')

    # Back to object mode so that we can select vertices
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a new bmesh from the object
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    # Find the lowest Z-coordinate among the vertices
    highest_z = max(v.co.z for v in bm.verts)

    # Select all vertices within the threshold of the lowest Z-coordinate
    selected_verts = []
    for v in bm.verts:
        if v.co.z > highest_z - threshold:
            v.select = True
            selected_verts.append(v)

    # Update the bmesh and mesh data
    bm.select_flush(True)
    bm.to_mesh(obj.data)
    obj.data.update()


# Function to clear the parent of an object
def object_parent_clear(obj):
    if obj is None:
        return

    # making we're in OBJECT mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Unparent the object while keeping its transforms
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


# Function to freeze transforms
def object_apply_transforms(obj):
    if obj is None:
        return

    # making we're in OBJECT mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Select obj and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Update the object data
    obj.data.update()


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

    # Update the mesh to show the selection
    bm.to_mesh(mesh_data)
    bm.free()

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')


def sort_vertices_by_distance_to_origin(vertex):
    mesh = vertex.id_data
    obj = [obj for obj in bpy.data.objects if obj.type == 'MESH'][0]
    world_coord = obj.matrix_world @ vertex.co
    distance_to_world_origin = world_coord.length
    return distance_to_world_origin


class VertexData(NamedTuple):
    coords: Vector
    vertices_count: int
    object: bpy.types.Object


def get_vertices_data_by_vertex_coords_closest_to_the_world_origin(obj):
    """returns (vertex_coords, vertices_count, obj)"""
    if obj is None:
        return

    vertices = list(obj.data.vertices)
    vertices.sort(key=sort_vertices_by_distance_to_origin)

    vertex_data = VertexData(coords=vertices[0].co, vertices_count=len(vertices), object=obj)

    return vertex_data


def sort_by_object_distance_to_origin(obj):
    return obj.location.length


def sort_by_vector_distance_to_origin(vector):
    return vector.length


def sort_by_vertices_data_vertex_coords_distance_to_origin(vertex_data):
    return vertex_data.coords.length


def get_scan_object(loose_obj_list):
    if not loose_obj_list:
        return

    parts = loose_obj_list

    vertices_data = [get_vertices_data_by_vertex_coords_closest_to_the_world_origin(obj) for obj in parts]

    vertices_data.sort(key=sort_by_vertices_data_vertex_coords_distance_to_origin)

    scan_obj = None
    for vertex_data in vertices_data:
        if vertex_data.vertices_count > 500:
            scan_obj = vertex_data.object
            scan_obj.name = 'g0' 
            break

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='SELECT')

    selected_objects_names = [obj.name for obj in bpy.context.selected_objects]

    for name in selected_objects_names:
        if name != scan_obj.name:
            bpy.data.objects.remove(bpy.data.objects.get(name))

    return scan_obj


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


def main(scan_ID=None, output_path=None, usdc_path=None):
    print_decorated("Executing the main() function in prepUSDZ.py...")

    # USED FOR TESTING
    ARGS = get_args()
    USE_LOCALLY = int(ARGS.use_locally)

    if USE_LOCALLY == 1:
        scan_ID = str(ARGS.scan)
        output_path = str(ARGS.path)

    usdc_path = os.path.join(output_path, "preview.usdz")

    if scan_ID is None or output_path is None or usdc_path is None:
        print_enhanced("main() FAILED | missing main arguments", text_color="red", label="ERROR", label_color="red")
        return

    print_decorated("Main Variables")
    print_enhanced(f"{scan_ID}", label="SCAN ID", label_color="cyan")
    print_enhanced(f"{output_path}", label="PATH", label_color="cyan")
    print_enhanced(f"{usdc_path}", label="USDC PATH", label_color="cyan")

    scene_clean_start()

    print_decorated("Starting Process")

    USDC_OBJ = import_usda_model(usdc_path)

    if USDC_OBJ is None:
        print_enhanced("main() FAILED | missing udsc object", text_color="red", label="ERROR", label_color="red")
        return

    # Check if the object exists
    if USDC_OBJ:
        # Clear parent and apply transforms of the object
        print_decorated("Clear Parenting and apply transforms of the object")
        object_parent_clear(USDC_OBJ)
        object_apply_transforms(USDC_OBJ)

        # Select the highest vertices and delete them
        select_highest_vertices(USDC_OBJ, 0.1)
        mesh_delete_selection(USDC_OBJ)

        # Remove the floor and separate by loose parts
        print_decorated("Remove and separate by loose parts")
        bmesh_select_faces_by_vector_direction(vector_direction=Vector((0,0,-1)), angle_threshold=175)
        mesh_delete_selection(USDC_OBJ, type='FACE')
        separate_object_loose_parts(USDC_OBJ)

        # To make sure each part origin is set
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        # Find the scanned person
        USDC_OBJ_PARTS = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        SCAN_OBJ = get_scan_object(USDC_OBJ_PARTS)

        if SCAN_OBJ is None:
            print_enhanced("main() FAILED | scan_obj is None", text_color="red", label="ERROR", label_color="red")
            return

        # Get the bounding box
        print_decorated("Getting Bounding Box")
        bounding_box = get_bounding_box(SCAN_OBJ, bboxOffset=0.4) # offset can be changed in case we need to push the bounding box further away from the object
        min_x, max_x, min_y, max_y, min_z, max_z = bounding_box

        print_decorated("Creating Bounding Box Keypoints")
        scan_obj_location = SCAN_OBJ.location

        create_empty_on_location("min_x", (min_x, scan_obj_location.y, scan_obj_location.z), link_to_collection="bounds")
        create_empty_on_location("max_x", (max_x, scan_obj_location.y, scan_obj_location.z), link_to_collection="bounds")
        create_empty_on_location("min_y", (scan_obj_location.x, min_y, scan_obj_location.z), link_to_collection="bounds")
        create_empty_on_location("max_y", (scan_obj_location.x, max_y, scan_obj_location.z), link_to_collection="bounds")
        create_empty_on_location("min_z", (scan_obj_location.x, scan_obj_location.y, min_z), link_to_collection="bounds")
        create_empty_on_location("max_z", (scan_obj_location.x, scan_obj_location.y, max_z), link_to_collection="bounds")

        print_decorated("Saving")
        if scan_ID and output_path:
            output_filepath = os.path.join(output_path, f"{scan_ID}_bounding_box.blend")
            save_as(output_filepath)

        # Print the bounding box coordinates
        print_decorated("Bounding Box Coords")
        print_enhanced(f"{min_x}", label="min x", label_color="cyan")
        print_enhanced(f"{max_x}", label="max x", label_color="cyan")
        print_enhanced(f"{min_y}", label="min y", label_color="cyan")
        print_enhanced(f"{max_y}", label="max y", label_color="cyan")
        print_enhanced(f"{min_z}", label="min z", label_color="cyan")
        print_enhanced(f"{max_z}", label="max z", label_color="cyan")

        return (min_x, max_x, min_y, max_y, min_z, max_z)

if __name__ == "__main__":
    main()