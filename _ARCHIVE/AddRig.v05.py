import os
import bpy
import math
import numpy
import argparse
from typing import NamedTuple
from mathutils import Vector
from dataclasses import dataclass


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ AddRig.v05 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ 09.25.2023 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
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

# IMAGES
def pack_textures():
    print_enhanced("Packing Textures", label="INFO", label_color="yellow")
    for image in bpy.data.images:
        if not image.packed_file:
            image.pack()

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

# CURSOR
def set_cursor_location(location=(0,0,0)):
    bpy.context.scene.cursor.location = location


# OBJECTS
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


def object_add_corrective_smooth_modifier(obj, name="CorrectiveSmooth", iterations=10):
    print_enhanced(f"object_add_corrective_smooth_modifier | obj: {obj.name} | iterations: {iterations}", label=f"INFO", label_color="yellow")

    if obj is None:
        return
    
    modifier = obj.modifiers.new(name, 'CORRECTIVE_SMOOTH')
    modifier.iterations = iterations

    return modifier


# COLLECTIONS
def collection_find(name):
    """returns None if not found"""
    data = bpy.data
    collections = data.collections

    collection = None

    for collection in collections:
        if name == collection.name:
            print_enhanced(f"{collection.name}", label="FOUND COLLECTION", label_color="green")
            return collection


def move_object_to_collection(obj, collection_name):
    #print_enhanced(f"move_to_collection | collection_name: {collection_name}", label="INFO", label_color="yellow")

    # Get the collection to move the object to
    collection = bpy.data.collections.get(collection_name)
    
    # If the collection doesn't exist, create it and link it to the scene
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        print_enhanced(f"'{collection_name}' created", label=f"COLLECTION", label_color="yellow")

    # if the object is not orphan, remove it from the collections
    if obj.users_collection:
        for user_collection in obj.users_collection:
            user_collection.objects.unlink(obj)

    # Move the object to the collection
    collection.objects.link(obj)
    print_enhanced(f"Linked to collection: {collection_name}", label=f"'{obj.name}' OBJECT", label_color="green")


def remove_collection(collection_name, remove_all_objects=True, log_ID=0):
    collection = bpy.data.collections.get(collection_name)

    if collection:
        if remove_all_objects:
            for obj in collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.collections.remove(collection)
        print_enhanced(f"{collection_name}", label="REMOVING COLLECTION", label_color="yellow")


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


def append_scan_object(filepath):
    append_collection(filepath, "geo")
    scan_obj = bpy.context.scene.objects.get("g0")

    if scan_obj is None:
        print_enhanced(f"append_scan failed | scan_obj is None", text_color="red", label="ERROR", label_color="red")
        return None

    if scan_obj.type != 'MESH':
        print_enhanced(f"append_scan failed | scan_obj is not type MESH", text_color="red", label="ERROR", label_color="red")
        return None

    print_enhanced(f"{scan_obj}", label="FOUND SCAN OBJECT", label_color="cyan", suffix="\n")
    return scan_obj


def append_armature(filepath, armature_name="Armature", reset_cursor_location=True):

    if reset_cursor_location:
        set_cursor_location(location=(0,0,0))

    directory = os.path.join(os.path.join(filepath, "Object/"))
    bpy.ops.wm.append(
    filepath=filepath,
    directory=directory,
    filename=armature_name)

    armature_obj = bpy.context.scene.objects.get("Armature")
    if armature_obj is None:
        print_enhanced(f"append_collection failed | armature_obj is None", text_color="red", label="ERROR", label_color="red")
        return None
    
    print_enhanced(f"collection '{armature_name}' from {directory}", label="APPEND COLLECTION", label_color="green")
    return armature_obj


# OS
def file_read_lines(filepath):
    if not os.path.exists(filepath):
        return []
    
    with open(filepath) as file:
        return file.readlines()


def save_as(filepath):
    try:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
    except Exception as e:
        print_enhanced(f"save_as failed | ERROR: {e}", text_color="red", label="ERROR", label_color="red")


# PROPERTIES
class Point(NamedTuple):
    x: float
    y: float
    z: float

    def to_vector(self, offset_vector=Vector((0,0,0))):
        return Vector((self.x + offset_vector.x, self.y + offset_vector.y, self.z + offset_vector.z))


@dataclass
class BodyPart:
    name: str
    point_mid: Point
    point_front: Point
    point_back: Point

    def to_tuple(self):
        return self.name, self.point_mid, self.point_front, self.point_back


# SORTING
def sort_coordinates_by_x(co):
    return co.x

def sort_coordinates_by_y(co):
    return co.y

def sort_coordinates_by_z(co):
    return co.z

def sort_vector_by_x(vector):
    return vector.x

def sort_vector_by_y(vector):
    return vector.y

def sort_vector_by_z(vector):
    return vector.z


# LOCATIONS & VECTORS & POINTS
def find_middle_location(locations, debug=False):
    if not locations:
        print_enhanced("find_middle_location failed | locations = None", text_color="red", label="ERROR", label_color="red")
        return
    if debug:
        print_enhanced(f"find_middle_location | locations: {locations}", label="INFO", label_color="yellow")

    # Calculate the sum of all locations
    total_loc = Vector((0.0, 0.0, 0.0))
    for location in locations:
        total_loc += Vector(location)
    
    # Calculate the middle location by dividing the sum by the number of locations
    middle_loc = total_loc / len(locations)
    
    if debug:
        print_enhanced(f"{middle_loc}", label="MIDDLE LOCATION", label_color="green")
    
    return middle_loc


def find_middle_point_using_locations(locations, debug=False):
    x, y, z = find_middle_location(locations, debug)
    return Point(x, y, z)


def find_middle_point(points, debug=False):
    locations = [tuple(point) for point in points]
    x, y, z = find_middle_location(locations, debug)
    return Point(x, y, z)


def find_front_and_back_vertices_points(obj, body_part:BodyPart, debug=False):
    if obj is None or not body_part:
        return Point(0,0,0), Point(0,0,0)
    
    if debug:
        print_enhanced(f"find_front_and_back_vertices_points | obj: {obj.name} | point_mid: {body_part.point_mid} |", label=f"{body_part.name}", label_color="yellow")

    obj_data = obj.data

    selection_threshold = 0.015

    vertices_coords = [
    obj.matrix_world @ v.co for v in obj_data.vertices if 
        v.co.z > body_part.point_mid.z - selection_threshold and v.co.z < body_part.point_mid.z + selection_threshold and 
        v.co.x > body_part.point_mid.x - selection_threshold and v.co.x < body_part.point_mid.x + selection_threshold]

    if len(vertices_coords) < 2:
        print_enhanced("find_front_and_back_vertices_points | len(vertices_coords) < 2", text_color="red", label=f"{body_part.name}", label_color="red")
        return Point(0,0,0), Point(0,0,0)

    # Sort the locations along y-axis
    vertices_coords.sort(key=sort_coordinates_by_y)

    # The point with the lowest y-coordinate
    point_front = Point(body_part.point_mid.x, vertices_coords[0].y, body_part.point_mid.z)

    # The point with the highest y-coordinate
    point_back = Point(body_part.point_mid.x, vertices_coords[-1].y, body_part.point_mid.z)

    return point_front, point_back


def find_object_max_z(obj):
    if obj is None:
        return

    bounds = [obj.matrix_world @ Vector(bound) for bound in obj.bound_box]
    bounds.sort(key=sort_vector_by_z)

    return bounds[-1].z


def divide_space_between_two_locations(location_start, location_end, n_parts):
    """
    Divides the space between two locations into n equal parts and return a list of all divided locations.
    
    Note: This function will return `n_parts` number of points, not `n_parts - 1` segments. 
    If you want the number of segments to be `n_parts`, you should use `n_parts + 1` when calling this function.
    """
    start_vec = Vector(location_start)
    end_vec = Vector(location_end)
    return [(start_vec + (end_vec - start_vec) * i / (n_parts - 1)).to_tuple() for i in range(n_parts)]


def divide_space_between_two_points(point_start, point_end, n_parts):
    result = divide_space_between_two_locations(point_start, point_end, n_parts)
    return [Point(*vector) for vector in result]


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN FUNCTIONS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def get_feet_points(scan_obj, left_ankle, right_ankle, desired_height=0.016):
    if scan_obj is None:
        return

    obj_data = scan_obj.data
    vertices = obj_data.vertices

    right_toe_tip_point = None
    left_toe_tip_point = None
    right_foot_heel_point = None
    left_foot_heel_point = None
    left_toe_base = None
    right_toe_base = None

    # Get all the vertices that represent the left foot, sorted by the y-coordinate
    left_foot_coords_list = [v.co for v in vertices if v.co.z < 0.01 and v.co.x > 0]
    left_foot_coords_list.sort(key=sort_coordinates_by_y)
    
    # The left toe tip is the vertex with the lowest y-coordinate
    if left_foot_coords_list:
        left_toe_tip_point = Point(left_foot_coords_list[0].x, left_foot_coords_list[0].y, desired_height)
        
        # The heel point is the vertex with the highest y-coordinate
        left_foot_heel_point = Point(left_foot_coords_list[-1].x, left_foot_coords_list[-1].y, desired_height)

    # Do the same for the right foot
    right_foot_coords_list = [v.co for v in vertices if v.co.z < 0.01 and v.co.x < 0]
    right_foot_coords_list.sort(key=sort_coordinates_by_y)

    if right_foot_coords_list:
        right_toe_tip_point = Point(right_foot_coords_list[0].x, right_foot_coords_list[0].y, desired_height)
        right_foot_heel_point = Point(right_foot_coords_list[-1].x, right_foot_coords_list[-1].y, desired_height)

    # If we have information about the ankle points, calculate the middle point between the toe tips and the ankle points
    if left_ankle is not None and right_ankle is not None:
        if left_toe_tip_point:
            left_toe_base = find_middle_point((left_toe_tip_point, left_ankle.point_mid))
        if right_toe_tip_point:
            right_toe_base = find_middle_point((right_toe_tip_point, right_ankle.point_mid))

    return left_toe_tip_point, right_toe_tip_point, left_foot_heel_point, right_foot_heel_point, left_toe_base, right_toe_base


def get_feet_sole_mid_points(scan_obj):
    if scan_obj is None:
        return

    obj_data = scan_obj.data
    vertices = obj_data.vertices

    # Get all the vertices that represent the left foot
    left_foot_coords = [v.co for v in vertices if v.co.z < 0.01 and v.co.x > 0]

    # Do the same for the right foot
    right_foot_coords = [v.co for v in vertices if v.co.z < 0.01 and v.co.x < 0]

    if left_foot_coords and right_foot_coords:
        left_foot_mid_point = find_middle_point(left_foot_coords)
        right_foot_mid_point = find_middle_point(right_foot_coords)
        return left_foot_mid_point, right_foot_mid_point
    
    if left_foot_coords and not right_foot_coords:
        left_foot_mid_point = find_middle_point(left_foot_coords)
        x, y, z = left_foot_mid_point
        right_foot_mid_point = Point(-x, y, z)
        return left_foot_mid_point, right_foot_mid_point

    if right_foot_coords and not left_foot_coords:
        right_foot_mid_point = find_middle_point(left_foot_coords)
        x, y, z = right_foot_mid_point
        left_foot_mid_point = Point(-x, y, z)
        return left_foot_mid_point, right_foot_mid_point


def get_body_parts_from_keypoints(results_filepath):
    print_enhanced(f"get_body_parts_from_keypoints | results_filepath: {results_filepath}", label=f"INFO", label_color="yellow")

    lines = file_read_lines(results_filepath)
    if not lines:
        return []
    pose_generator_data = [line.split(" ") for line in lines]
    body_parts = []

    for name, x, z in pose_generator_data:
        body_part = BodyPart(name.lower(), point_mid=Point(float(x), 0.0, float(z)), point_front=Point(0,0,0), point_back=Point(0,0,0))
        body_parts.append(body_part)

    for part in body_parts:
        print_enhanced(f"{part.point_mid}", label=f"{part.name}", label_color="cyan")

    return body_parts


def update_body_parts_data(scan_obj, body_parts:BodyPart):
    print_enhanced(f"update_body_parts_data | scan_obj: {scan_obj.name}", label=f"INFO", label_color="yellow", prefix="\n")

    if scan_obj is None:
        return []

    if not body_parts:
        return []
    
    # Initialize lists for different body parts
    mouth_parts = []
    arm_parts = []
    left_fingers_parts = []
    right_fingers_parts = []
    left_hip_part = None
    right_hip_part = None
    left_elbow_part = None
    left_wrist_part = None
    right_elbow_part = None
    right_wrist_part = None
    left_ankle_part = None
    right_ankle_part = None

    parts_to_remove = []
    parts_to_add = []

    # .- In case LEFT_ANKLE or RIGHT_ANKLE point_mid = 0,0,0
    left_ankle_fake_point, right_ankle_fake_point = get_feet_sole_mid_points(scan_obj)
    foot_ankle_fake_height = 0.032
    
    for body_part in body_parts:
        # Ignore foot index since we already got a better way to find the foot points
        if "foot_index" in body_part.name:
            continue

        # Find front, back, and middle points
        # FIXME: There may be cases where the mesh has a closed hole and few vertices, meaning that it won't be able to find the right points, maybe instead of doing it by directly finding the vertices I could use bisect to cut a line of vertices and use those instead
        point_front, point_back = find_front_and_back_vertices_points(scan_obj, body_part)
        point_mid = find_middle_point_using_locations((point_front, point_back))
        body_part.point_mid = point_mid
        body_part.point_front = point_front
        body_part.point_back = point_back

        # Classify body parts based on their name
        if "mouth" in body_part.name:
            mouth_parts.append(body_part)

        # RIGHT AND LEFT ARMS: finding shoulder parts, changing the name to arms (since the parts are actually the arms head) and appending it to arms_parts
        if "shoulder" in body_part.name:
            body_part.name = body_part.name.replace("shoulder", "arm")
            arm_parts.append(body_part)

        if any(word in body_part.name for word in ("left_pinky", "left_index", "left_thumb")):
            left_fingers_parts.append(body_part)

        if any(word in body_part.name for word in ("right_pinky", "right_index", "right_thumb")):
            right_fingers_parts.append(body_part)

        if "left_elbow" in body_part.name:
            left_elbow_part = body_part

        if "right_elbow" in body_part.name:
            right_elbow_part = body_part

        if "left_wrist" in body_part.name:
            left_wrist_part = body_part

        if "right_wrist" in body_part.name:
            right_wrist_part = body_part

        if "left_hip" in body_part.name:
            left_hip_part = body_part

        if "right_hip" in body_part.name:
            right_hip_part = body_part

        if "left_ankle" == body_part.name:
            if body_part.point_mid.to_vector().length == 0 or body_part.point_mid.z > 0.25:
                # Remove after this loop
                parts_to_remove.append(body_part)

                # Fake ankle part
                left_ankle_part = BodyPart(f"{body_part.name}", point_mid=Point(left_ankle_fake_point.x, left_ankle_fake_point.y, foot_ankle_fake_height), point_front=Point(0,0,0), point_back=Point(0,0,0))
                
                # Add new part after this loop
                parts_to_add.append(left_ankle_part)
                print_enhanced(f"point_mid is 0, using fake point instead | point: {left_ankle_part.point_mid}", label=f"{left_ankle_part.name}", label_color="green")
            else:
                left_ankle_part = body_part

        if "right_ankle" == body_part.name:
            if body_part.point_mid.to_vector().length == 0 or body_part.point_mid.z > 0.25:
                # Remove after this loop
                parts_to_remove.append(body_part)
                
                # Fake ankle part
                right_ankle_part = BodyPart(f"{body_part.name}", point_mid=Point(right_ankle_fake_point.x, right_ankle_fake_point.y, foot_ankle_fake_height), point_front=Point(0,0,0), point_back=Point(0,0,0))
                
                # Add new part after this loop
                parts_to_add.append(right_ankle_part)
                print_enhanced(f"point_mid is 0, using fake point instead | point: {right_ankle_part.point_mid}", label=f"{right_ankle_part.name}", label_color="green")
            else:
                right_ankle_part = body_part

    body_parts = [body_part for body_part in body_parts if body_part not in parts_to_remove] + parts_to_add

    # Compute shoulder points by dividing space between two arm parts
    shoulder_points = divide_space_between_two_points(point_start=arm_parts[0].point_mid, point_end=arm_parts[1].point_mid, n_parts=5)
    shoulder_left_point = shoulder_points[1]
    shoulder_mid_point = shoulder_points[2]
    shoulder_right_point = shoulder_points[3]

    # Calculate mouth mid points
    mouth_mid_point = find_middle_point_using_locations([part.point_mid for part in mouth_parts])
    mouth_shoulder_mid_point = find_middle_point_using_locations((shoulder_mid_point, mouth_mid_point))
    mouth_front_mid_point = find_middle_point_using_locations([part.point_front for part in mouth_parts])
    mouth_back_mid_point = find_middle_point_using_locations([part.point_back for part in mouth_parts])

    # Calculate fingers mid points
    left_fingers_mid_point = find_middle_point([part.point_mid for part in left_fingers_parts])
    right_fingers_mid_point = find_middle_point([part.point_mid for part in right_fingers_parts])
    
    scan_max_z = find_object_max_z(scan_obj)
    head_top_mid_point = Point(mouth_mid_point.x, mouth_mid_point.y, scan_max_z)    

    # Compute spine points
    hip_mid_point = find_middle_point_using_locations([left_hip_part.point_mid, right_hip_part.point_mid])
    spine_division_points = divide_space_between_two_points(point_start=hip_mid_point, point_end=shoulder_mid_point, n_parts=5)

    # Compute feet points
    feet_points_height = 0.016
    left_toe_tip_point, right_toe_tip_point, left_foot_heel_point, right_foot_heel_point, left_toe_base_point, right_toe_base_point = get_feet_points(scan_obj, left_ankle_part, right_ankle_part, desired_height=feet_points_height)

    # Compute average point between shoulder_mid, spines and hip
    # This is to have a centered straight line of points
    spine_complete_points = [shoulder_mid_point, hip_mid_point] + spine_division_points
    spine_mid_point = find_middle_point(spine_complete_points)

    # Set shoulder_mid, hip_mid and spine_points x, y values to the spine_mid x, y values
    spine_division_points = [Point(spine_mid_point.x, spine_mid_point.y, point.z) for point in spine_division_points]
    shoulder_mid_point = Point(spine_mid_point.x, spine_mid_point.y, shoulder_mid_point.z)
    hip_mid_point = Point(spine_mid_point.x, spine_mid_point.y, hip_mid_point.z)

    # Compute corrective bones
    shoulder_left_top = Point(shoulder_left_point.x, shoulder_left_point.y, mouth_shoulder_mid_point.z)
    shoulder_right_top = Point(shoulder_right_point.x, shoulder_right_point.y, mouth_shoulder_mid_point.z)

    # z = spine1_mid.z + ((spine2_mid.z - spine1_mid.z) / 2) | spine1_mid height + half the distance between spine2_mid and spine1_mid
    armpit_z = spine_division_points[2].z + ((spine_division_points[3].z - spine_division_points[2].z) / 2)

    armpit_left_point = Point(arm_parts[0].point_mid.x, arm_parts[0].point_mid.y, armpit_z)
    armpit_right_point = Point(arm_parts[1].point_mid.x, arm_parts[1].point_mid.y, armpit_z)

    # forearms
    left_forearm_division_points = divide_space_between_two_points(point_start=left_elbow_part.point_mid, point_end=left_wrist_part.point_mid, n_parts=4)
    right_forearm_division_points = divide_space_between_two_points(point_start=right_elbow_part.point_mid, point_end=right_wrist_part.point_mid, n_parts=4)

    # Hips
    hips_fix_height = hip_mid_point.z + ((spine_division_points[1].z - hip_mid_point.z) / 2)
    hip_fix_left_point = Point(left_hip_part.point_mid.x, left_hip_part.point_mid.y, hips_fix_height)
    hip_fix_right_point = Point(right_hip_part.point_mid.x, right_hip_part.point_mid.y, hips_fix_height)

    # Add additional body parts
    point_zero = Point(0,0,0)
    body_parts.append(BodyPart("left_shoulder", shoulder_left_point, point_zero, point_zero))
    body_parts.append(BodyPart("mid_shoulder", shoulder_mid_point, point_zero, point_zero))
    body_parts.append(BodyPart("right_shoulder", shoulder_right_point, point_zero, point_zero))

    body_parts.append(BodyPart("mouth_mid", mouth_mid_point, point_zero, point_zero))
    body_parts.append(BodyPart("mouth_shoulder_mid", mouth_shoulder_mid_point, point_zero, point_zero))
    body_parts.append(BodyPart("mouth_front_mid", Point(mouth_mid_point.x, mouth_front_mid_point.y, mouth_mid_point.z), point_zero, point_zero))
    body_parts.append(BodyPart("mouth_back_mid", Point(mouth_mid_point.x, mouth_back_mid_point.y, mouth_mid_point.z), point_zero, point_zero))

    body_parts.append(BodyPart("left_fingers_mid", left_fingers_mid_point, point_zero, point_zero))
    body_parts.append(BodyPart("right_fingers_mid", right_fingers_mid_point, point_zero, point_zero))

    body_parts.append(BodyPart("head_top_mid", head_top_mid_point, point_zero, point_zero))

    body_parts.append(BodyPart("hip_mid", hip_mid_point, point_zero, point_zero))

    body_parts.append(BodyPart("left_hip_fix", hip_fix_left_point, point_zero, point_zero))
    body_parts.append(BodyPart("right_hip_fix", hip_fix_right_point, point_zero, point_zero))

    if left_toe_tip_point is not None:
        body_parts.append(BodyPart("left_toe_tip", left_toe_tip_point, point_zero, point_zero))

        # Mirror left point into right point in case right is missing
        if right_toe_tip_point is None:
            body_parts.append(BodyPart("right_toe_tip", Point(-left_toe_tip_point.x, left_toe_tip_point.y, left_toe_tip_point.z), point_zero, point_zero))

    if right_toe_tip_point is not None:
        body_parts.append(BodyPart("right_toe_tip", right_toe_tip_point, point_zero, point_zero))

        # Mirror right point into left point in case left is missing
        if left_toe_tip_point is None:
            body_parts.append(BodyPart("left_toe_tip", Point(-right_toe_tip_point.x, right_toe_tip_point.y, right_toe_tip_point.z), point_zero, point_zero))

    if left_foot_heel_point is not None:
        body_parts.append(BodyPart("left_foot_heel", left_foot_heel_point, point_zero, point_zero))

        # Mirror left point into right point in case right is missing
        if right_foot_heel_point is None:
            body_parts.append(BodyPart("right_foot_heel", Point(-left_foot_heel_point.x, left_foot_heel_point.y, left_foot_heel_point.z), point_zero, point_zero))

    if right_foot_heel_point is not None:
        body_parts.append(BodyPart("right_foot_heel", right_foot_heel_point, point_zero, point_zero))

        # Mirror right point into left point in case left is missing
        if left_foot_heel_point is None:
            body_parts.append(BodyPart("left_foot_heel", Point(-right_foot_heel_point.x, right_foot_heel_point.y, right_foot_heel_point.z), point_zero, point_zero))

    body_parts.append(BodyPart("left_shoulder_top", shoulder_left_top, point_zero, point_zero))
    body_parts.append(BodyPart("right_shoulder_top", shoulder_right_top, point_zero, point_zero))

    body_parts.append(BodyPart("right_armpit", armpit_right_point, point_zero, point_zero))
    body_parts.append(BodyPart("left_armpit", armpit_left_point, point_zero, point_zero))

    if left_toe_base_point is not None:
        body_parts.append(BodyPart("left_toe_base", Point(left_toe_base_point.x, left_toe_base_point.y, feet_points_height), point_zero, point_zero))

        # Mirror left point into right point in case right is missing
        if right_toe_base_point is None:
            body_parts.append(BodyPart("right_toe_base", Point(-left_toe_base_point.x, left_toe_base_point.y, feet_points_height), point_zero, point_zero))

    if right_toe_base_point is not None:
        body_parts.append(BodyPart("right_toe_base", Point(right_toe_base_point.x, right_toe_base_point.y, feet_points_height), point_zero, point_zero))

        # Mirror right point into left point in case left is missing
        if left_toe_base_point is None:
            body_parts.append(BodyPart("left_toe_base", Point(-right_toe_base_point.x, right_toe_base_point.y, feet_points_height), point_zero, point_zero))

    # Add spine points
    for i, forearm_location in enumerate(spine_division_points):
        if i == 0 or i == len(spine_division_points) - 1:
            continue
        body_parts.append(BodyPart(f"spine{i-1}_mid", Point(*forearm_location), point_zero, point_zero))

    # Forearms
    for i, forearm_location in enumerate(left_forearm_division_points):
        if i == 0 or i == len(left_forearm_division_points) - 1:
            continue
        body_parts.append(BodyPart(f"left_forearm{i-1}_mid", Point(*forearm_location), point_zero, point_zero))

    for i, forearm_location in enumerate(right_forearm_division_points):
        if i == 0 or i == len(left_forearm_division_points) - 1:
            continue
        body_parts.append(BodyPart(f"right_forearm{i-1}_mid", Point(*forearm_location), point_zero, point_zero))

    print_enhanced(f"Updated Body Parts", label=f"INFO", label_color="yellow", prefix="\n")
    for part in body_parts:
        print_enhanced(f"{part.point_mid}", label=f"{part.name}", label_color="green")

    return body_parts


def snap_bones(armature, body_parts):
    print_enhanced(f"snap_bones | armature: {armature.name}", label=f"INFO", label_color="yellow")

    if armature is None or not body_parts:
        return
    
    armature.show_in_front = True

    # update this list whenever a new body_part is added in the update_body_parts_data function 
    body_part_names = [
    "head_top_mid",
    "left_ear",
    "right_ear",
    "nose",
    "mouth_mid",
    "mouth_shoulder_mid",
    "mouth_front_mid",
    "mouth_back_mid",
    "left_shoulder_top",
    "left_shoulder",
    "mid_shoulder",
    "right_shoulder",
    "right_shoulder_top",
    "left_arm",
    "right_arm",
    "left_armpit",
    "right_armpit",
    "spine2_mid",
    "spine1_mid",
    "spine0_mid",
    "left_elbow",
    "left_forearm0_mid",
    "left_forearm1_mid",
    "right_elbow",
    "right_forearm0_mid",
    "right_forearm1_mid",
    "left_wrist",
    "right_wrist",
    "left_fingers_mid",
    "right_fingers_mid",
    "left_hip_fix",
    "left_hip",
    "hip_mid",
    "right_hip",
    "right_hip_fix",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_toe_tip",
    "left_toe_base",
    "left_foot_heel",
    "right_toe_tip",
    "right_toe_base",
    "right_foot_heel",
    ]

    # Creating body parts dictionary using body_part_names
    print_enhanced(f"snap_bones | Creating body parts dictionary using body_part_names", label=f"INFO", label_color="yellow")
    body_parts_map = {name: None for name in body_part_names}

    for body_part in body_parts:
        if body_part.name in body_parts_map:
            body_parts_map[body_part.name] = body_part

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT') 

    bpy.ops.object.select_all(action='DESELECT')

    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.data.edit_bones

    head_offset = Vector((0, 0, 0.05))
    head_to_jaw_offset = Vector((0, 0, abs(body_parts_map["nose"].point_mid.z - body_parts_map["mouth_mid"].point_mid.z)))
    jaw_offset = Vector((0, -0.02, 0))
    neck_offset = Vector((0, 0, 0.04))
    shoulder_top_offset = Vector((0, 0, 0.03))
    armpit_offset = Vector((0, 0, 0.03))

    hip_fix_offset = Vector((0, 0, 0.03))

    half_length_from_mid_to_front_left_knee = (body_parts_map["left_knee"].point_front.y - body_parts_map["left_knee"].point_mid.y) / 2
    left_leg_offset = Vector((0, half_length_from_mid_to_front_left_knee, 0))
    
    half_length_from_mid_to_front_right_knee = (body_parts_map["right_knee"].point_front.y - body_parts_map["right_knee"].point_mid.y) / 2
    right_leg_offset = Vector((0, half_length_from_mid_to_front_right_knee, 0))

    left_upleg_front_fix_point = Point(body_parts_map["left_hip"].point_mid.x, body_parts_map["left_hip"].point_front.y - body_parts_map["left_hip"].point_mid.y, body_parts_map["left_hip"].point_mid.z)
    left_upleg_back_fix_point = Point(body_parts_map["left_hip"].point_mid.x, abs(body_parts_map["left_hip"].point_mid.y - body_parts_map["left_hip"].point_back.y), body_parts_map["left_hip"].point_mid.z)

    right_upleg_front_fix_offset = Point(body_parts_map["right_hip"].point_mid.x, body_parts_map["right_hip"].point_front.y - body_parts_map["right_hip"].point_mid.y, body_parts_map["right_hip"].point_mid.z)
    right_upleg_back_fix_offset = Point(body_parts_map["right_hip"].point_mid.x, abs(body_parts_map["right_hip"].point_mid.y - body_parts_map["right_hip"].point_back.y), body_parts_map["right_hip"].point_mid.z)

    left_ear_point = Point(body_parts_map["left_shoulder_top"].point_mid.x, body_parts_map["nose"].point_mid.y, body_parts_map["left_ear"].point_mid.z)
    right_ear_point = Point(body_parts_map["right_shoulder_top"].point_mid.x, body_parts_map["nose"].point_mid.y, body_parts_map["right_ear"].point_mid.z)

    # Snap bones head and tail using body_parts data from body_parts_map
    print_enhanced(f"snap_bones | Snap bones head and tail using body_parts data from body_parts_map", label=f"INFO", label_color="yellow")
    for bone in edit_bones:
        if bone.name == "mixamorig:LeftEar":
            bone.head = left_ear_point.to_vector()
            bone.tail = left_ear_point.to_vector(offset_vector=shoulder_top_offset)

        if bone.name == "mixamorig:RightEar":
            bone.head = right_ear_point.to_vector()
            bone.tail = right_ear_point.to_vector(offset_vector=shoulder_top_offset)

        if bone.name == "mixamorig:Head":
            bone.head = body_parts_map["mouth_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["head_top_mid"].point_mid.to_vector(offset_vector=head_offset)

        if bone.name == "mixamorig:HeadToJaw0":
            bone.head = body_parts_map["head_top_mid"].point_mid.to_vector(offset_vector=head_offset)
            bone.tail = body_parts_map["mouth_back_mid"].point_mid.to_vector(offset_vector=head_to_jaw_offset)

        if bone.name == "mixamorig:HeadToJaw1":
            bone.head = body_parts_map["mouth_back_mid"].point_mid.to_vector(offset_vector=head_to_jaw_offset)
            bone.tail = body_parts_map["mouth_mid"].point_mid.to_vector(offset_vector=jaw_offset)

        if bone.name == "mixamorig:Jaw":
            bone.head = body_parts_map["mouth_mid"].point_mid.to_vector(offset_vector=jaw_offset)
            bone.tail = body_parts_map["mouth_front_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:Neck":
            bone.head = body_parts_map["mouth_shoulder_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["mouth_shoulder_mid"].point_mid.to_vector(neck_offset)

        if bone.name == "mixamorig:Neck_BackFix":
            bone.head = body_parts_map["mouth_back_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["mouth_back_mid"].point_mid.to_vector(neck_offset)

        if bone.name == "mixamorig:LeftShoulder":
            bone.head = body_parts_map["left_shoulder"].point_mid.to_vector()
            bone.tail = body_parts_map["left_arm"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftShoulderTop":
            bone.head = body_parts_map["left_shoulder_top"].point_mid.to_vector()
            bone.tail = body_parts_map["left_shoulder_top"].point_mid.to_vector(shoulder_top_offset)

        if bone.name == "mixamorig:RightShoulder":
            bone.head = body_parts_map["right_shoulder"].point_mid.to_vector()
            bone.tail = body_parts_map["right_arm"].point_mid.to_vector()

        if bone.name == "mixamorig:RightShoulderTop":
            bone.head = body_parts_map["right_shoulder_top"].point_mid.to_vector()
            bone.tail = body_parts_map["right_shoulder_top"].point_mid.to_vector(shoulder_top_offset)

        if bone.name == "mixamorig:RightArmpit":
            bone.head = body_parts_map["right_armpit"].point_mid.to_vector()
            bone.tail = body_parts_map["right_armpit"].point_mid.to_vector(armpit_offset)

        if bone.name == "mixamorig:LeftArmpit":
            bone.head = body_parts_map["left_armpit"].point_mid.to_vector()
            bone.tail = body_parts_map["left_armpit"].point_mid.to_vector(armpit_offset)

        if bone.name == "mixamorig:LeftArm":
            bone.head = body_parts_map["left_arm"].point_mid.to_vector()
            bone.tail = body_parts_map["left_elbow"].point_mid.to_vector()

        if bone.name == "mixamorig:RightArm":
            bone.head = body_parts_map["right_arm"].point_mid.to_vector()
            bone.tail = body_parts_map["right_elbow"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftForeArm":
            bone.head = body_parts_map["left_elbow"].point_mid.to_vector()
            bone.tail = body_parts_map["left_forearm0_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftForeArm1":
            bone.head = body_parts_map["left_forearm0_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["left_forearm1_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftForeArm2":
            bone.head = body_parts_map["left_forearm1_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["left_wrist"].point_mid.to_vector()

        if bone.name == "mixamorig:RightForeArm":
            bone.head = body_parts_map["right_elbow"].point_mid.to_vector()
            bone.tail = body_parts_map["right_forearm0_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:RightForeArm1":
            bone.head = body_parts_map["right_forearm0_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["right_forearm1_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:RightForeArm2":
            bone.head = body_parts_map["right_forearm1_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["right_wrist"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftHand":
            bone.head = body_parts_map["left_wrist"].point_mid.to_vector()
            bone.tail = body_parts_map["left_fingers_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:RightHand":
            bone.head = body_parts_map["right_wrist"].point_mid.to_vector()
            bone.tail = body_parts_map["right_fingers_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:Hips":
            bone.head = body_parts_map["hip_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["spine0_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftHip_Fix":
            bone.head = body_parts_map["left_hip_fix"].point_mid.to_vector()
            bone.tail = body_parts_map["left_hip_fix"].point_mid.to_vector(hip_fix_offset)

        if bone.name == "mixamorig:RightHip_Fix":
            bone.head = body_parts_map["right_hip_fix"].point_mid.to_vector()
            bone.tail = body_parts_map["right_hip_fix"].point_mid.to_vector(hip_fix_offset)

        if bone.name == "mixamorig:Spine":
            bone.head = body_parts_map["spine0_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["spine1_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:Spine1":
            bone.head = body_parts_map["spine1_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["spine2_mid"].point_mid.to_vector()

        if bone.name == "mixamorig:Spine2":
            bone.head = body_parts_map["spine2_mid"].point_mid.to_vector()
            bone.tail = body_parts_map["mid_shoulder"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftUpLeg":
            bone.head = body_parts_map["left_hip"].point_mid.to_vector()
            bone.tail = body_parts_map["left_knee"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftUpLeg_FrontFix":
            bone.head = body_parts_map["left_hip"].point_mid.to_vector()
            bone.tail = left_upleg_front_fix_point.to_vector()

        if bone.name == "mixamorig:LeftUpLeg_BackFix":
            bone.head = body_parts_map["left_hip"].point_mid.to_vector()
            bone.tail = left_upleg_back_fix_point.to_vector()

        if bone.name == "mixamorig:RightUpLeg":
            bone.head = body_parts_map["right_hip"].point_mid.to_vector()
            bone.tail = body_parts_map["right_hip"].point_mid.to_vector()

        if bone.name == "mixamorig:RightUpLeg_FrontFix":
            bone.head = body_parts_map["right_hip"].point_mid.to_vector()
            bone.tail = right_upleg_front_fix_offset.to_vector()

        if bone.name == "mixamorig:RightUpLeg_BackFix":
            bone.head = body_parts_map["right_hip"].point_mid.to_vector()
            bone.tail = right_upleg_back_fix_offset.to_vector()

        if bone.name == "mixamorig:LeftLeg":
            bone.head = body_parts_map["left_knee"].point_mid.to_vector(left_leg_offset)
            bone.tail = body_parts_map["left_ankle"].point_mid.to_vector()

        if bone.name == "mixamorig:RightLeg":
            bone.head = body_parts_map["right_knee"].point_mid.to_vector(right_leg_offset)
            bone.tail = body_parts_map["right_ankle"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftFoot":
            bone.head = body_parts_map["left_ankle"].point_mid.to_vector()
            bone.tail = body_parts_map["left_toe_base"].point_mid.to_vector()

        if bone.name == "mixamorig:RightFoot":
            bone.head = body_parts_map["right_ankle"].point_mid.to_vector()
            bone.tail = body_parts_map["right_toe_base"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftToeBase":
            bone.head = body_parts_map["left_toe_base"].point_mid.to_vector()
            bone.tail = body_parts_map["left_toe_tip"].point_mid.to_vector()

        if bone.name == "mixamorig:RightToeBase":
            bone.head = body_parts_map["right_toe_base"].point_mid.to_vector()
            bone.tail = body_parts_map["right_toe_tip"].point_mid.to_vector()

        if bone.name == "mixamorig:LeftHeel":
            bone.head = body_parts_map["left_ankle"].point_mid.to_vector()
            bone.tail = body_parts_map["left_foot_heel"].point_mid.to_vector()

        if bone.name == "mixamorig:RightHeel":
            bone.head = body_parts_map["right_ankle"].point_mid.to_vector()
            bone.tail = body_parts_map["right_foot_heel"].point_mid.to_vector()

    # Fix bone rolls
    print_enhanced(f"snap_bones | Fixing bone rolls", label=f"INFO", label_color="yellow")
    bpy.ops.armature.select_all(action='DESELECT')
    for bone in edit_bones:
        if "Arm" in bone.name:
            bone.select = True
            bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Z')

        # Hardcoded left and right hands rolls
        if "LeftHand" in bone.name:
            bone.roll = math.radians(-35)

        if "RightHand" in bone.name:
            bone.roll = math.radians(7)

    bpy.ops.armature.select_all(action='DESELECT')
    for bone in edit_bones:
        if "RightFoot" in bone.name or "LeftFoot" in bone.name:
            bone.select = True
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')

    # Back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def scan_obj_rigging(scan_obj, armature):
    print_enhanced(f"scan_obj_rigging | scan_obj: {scan_obj.name} | armature: {armature.name}", label=f"INFO", label_color="yellow")

    if scan_obj is None or armature is None:
        return
    
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT') 

    bpy.ops.object.select_all(action='DESELECT')

    armature.select_set(True)
    scan_obj.select_set(True)

    bpy.context.view_layer.objects.active = armature

    armature.show_in_front = True
    
    print_enhanced(f"scan_obj_rigging | Automatic Weights", label=f"INFO", label_color="yellow")
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


all_keypoints = [
    "NOSE",
    "LEFT_EYE_INNER",
    "LEFT_EYE",
    "LEFT_EYE_OUTER",
    "RIGHT_EYE_INNER",
    "RIGHT_EYE",
    "RIGHT_EYE_OUTER",
    "LEFT_EAR",
    "RIGHT_EAR",
    "MOUTH_LEFT",
    "MOUTH_RIGHT",
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "LEFT_WRIST",
    "RIGHT_WRIST",
    "LEFT_PINKY",
    "RIGHT_PINKY",
    "LEFT_INDEX",
    "RIGHT_INDEX",
    "LEFT_THUMB",
    "RIGHT_THUMB",
    "LEFT_HIP",
    "RIGHT_HIP",
    "LEFT_KNEE",
    "RIGHT_KNEE",
    "LEFT_ANKLE",
    "RIGHT_ANKLE",
    "LEFT_HEEL",
    "RIGHT_HEEL",
    "LEFT_FOOT_INDEX",
    "RIGHT_FOOT_INDEX",
    ]

keypoints_to_ignore = [
    "LEFT_EYE",
    "LEFT_EYE_INNER",
    "LEFT_EYE_OUTER",
    "RIGHT_EYE",
    "RIGHT_EYE_INNER",
    "RIGHT_EYE_OUTER",
    "MOUTH_LEFT",
    "MOUTH_RIGHT",
    "LEFT_PINKY",
    "RIGHT_PINKY",
    "LEFT_INDEX",
    "RIGHT_INDEX",
    "LEFT_THUMB",
    "RIGHT_THUMB",
    "LEFT_HEEL",
    "RIGHT_HEEL",
    "LEFT_FOOT_INDEX",
    "RIGHT_FOOT_INDEX",
    ]


def main():
    print_decorated("MAIN VARIABLES")
    args = get_args()
    scan = str(args.scan)
    path = str(args.path)
    software_path = str(args.software)
    use_clean_start = int(args.clean_start)

    results_filepath = os.path.join(path, scan, "photogrammetry", f"{scan}_results.txt")
    scan_obj_filepath = os.path.join(path, scan, "photogrammetry", f"{scan}.blend")
    armature_filepath = os.path.join(software_path, "skeleton_template.blend")

    print_enhanced(path, label="PATH", label_color="cyan", prefix="\n")
    print_enhanced(scan, label="SCAN", label_color="cyan")
    print_enhanced(software_path, label="SOFTWARE", label_color="cyan")
    print_enhanced(use_clean_start, label="USE CLEAN START", label_color="cyan")

    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN STEPS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
    print_decorated("MAIN STEPS")

    if use_clean_start:
        scene_clean_start()

    # APPEND SCAN OBJECT
    print_decorated("APPEND SCAN OBJECT")
    scan_obj = append_scan_object(scan_obj_filepath)
    if scan_obj is None:
        print_enhanced("scan_obj is None", text_color="red", label="ERROR", label_color="red")
        return
    
    # FETCH AND UPDATE BODY PARTS
    print_decorated("FETCH AND UPDATE BODY PARTS")
    body_parts = get_body_parts_from_keypoints(results_filepath)
    body_parts_updated = update_body_parts_data(scan_obj, body_parts)

    # CREATE KEYPOINTS EMPTIES
    print_decorated("CREATE KEYPOINTS EMPTIES")
    keypoints = []
    keypoints_front = []
    for name, point_mid, point_front, point_back in (body_part.to_tuple() for body_part in body_parts_updated if body_part is not None):
        if name.upper() in keypoints_to_ignore:
            continue

        if point_mid is None:
            continue
        
        keypoint = create_empty_on_location(name=name, location=point_mid)
        keypoints.append(keypoint)
        
        keypoint_front = create_empty_on_location(name=f"{name}_front", location=point_front)
        keypoints_front.append(keypoint_front)

    # RIGGING
    print_decorated("RIGGING")
    armature = append_armature(armature_filepath)
    snap_bones(armature, body_parts_updated)
    scan_obj_rigging(scan_obj, armature)
    object_add_corrective_smooth_modifier(scan_obj)

    # ORGANIZING
    print_decorated("ORGANIZING")
    remove_collection("geo", remove_all_objects=False)
    move_object_to_collection(scan_obj, "rig")
    move_object_to_collection(armature, "rig")
    if keypoints:
        for keypoint in keypoints:
            move_object_to_collection(keypoint, "keypoints")

    if keypoints_front:
        for keypoint in keypoints_front:
            move_object_to_collection(keypoint, "keypoints_front")

    # SAVING
    print_decorated("SAVING")
    pack_textures()
    output_filepath = os.path.join(path, scan, "photogrammetry", f"{scan}-rig.blend")
    save_as(output_filepath)

if __name__ == "__main__":
    main()