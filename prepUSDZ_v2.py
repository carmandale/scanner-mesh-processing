import bpy
import bmesh
from mathutils import Vector

# This is the beginning of the preparation script for the USDZ file
# This script will be executed before the USDZ file is exported
# Need to add import of USDZ file and EXPORT of USDZ file
# Currently this script unparents the model, freezes transforms, and deletes the bottom and top vertices
# This script will import a USDZ file, delete the bottom and top vertices, get the bounding box of the person, and export a new USDZ file

def select_lowest_vertices(threshold):
    # Get the active object
    obj = bpy.context.active_object

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
    lowest_z = min(v.co.z for v in bm.verts)

    # Select all vertices within the threshold of the lowest Z-coordinate
    selected_verts = []
    for v in bm.verts:
        if v.co.z < lowest_z + threshold:
            v.select = True
            selected_verts.append(v)

    # Update the bmesh and mesh data
    bm.select_flush(True)
    bm.to_mesh(obj.data)
    obj.data.update()
    
    delete_vertices()

def select_highest_vertices(threshold):
    # Get the active object
    obj = bpy.context.active_object

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
    
    delete_vertices()
    
def delete_vertices():
    # Get the active object
    obj = bpy.context.active_object
    
    bpy.ops.object.mode_set(mode='EDIT') 

    bpy.ops.mesh.delete(type='VERT')
    
    # Back to object mode so that we can select vertices
    bpy.ops.object.mode_set(mode='OBJECT')

# Function to unparent an object
def unparent_object(obj):
    # Unparent the object while keeping its transforms
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

# Function to freeze transforms
def freeze_transforms(obj):
    # Freeze transforms
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Update the object data
    obj.data.update()


def select_vertices_near_origin(threshold):
    # Get the active object
    obj = bpy.context.active_object

    # Deselect all vertices
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    # Back to object mode so that we can select vertices
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a new bmesh from the object
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    # Find vertices near the origin within the threshold
    origin = Vector((0, 0, 0))
    selected_verts = []
    for v in bm.verts:
        if (v.co - origin).length < threshold:
            v.select = True
            selected_verts.append(v)

    # Update the bmesh and mesh data
    bm.select_flush(True)
    bm.to_mesh(obj.data)
    obj.data.update()

    # Select all linked vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_linked(delimit=set())

    # Get the bounding box of the selected vertices
    bbox = [v.co for v in bm.verts if v.select]
    bbox_min = Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
    bbox_max = Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
    bbox_center = (bbox_min + bbox_max) / 2

    # Print the bounding box
    print("Bounding box:")
    print(f"min: {bbox_min.to_tuple()}")
    print(f"max: {bbox_max.to_tuple()}")
    print(f"center: {bbox_center.to_tuple()}")

    return selected_verts

def get_bounding_box():

    # Get the active object
    obj = bpy.context.active_object

    # Select the vertices
    selected_verts = [v for v in obj.data.vertices if v.select]

    # Duplicate the selected vertices
    bpy.ops.mesh.duplicate()

    # Separate the mesh by selection
    bpy.ops.mesh.separate(type='SELECTED')

    # Deselect the original object
    obj.select_set(False)
    bpy.context.view_layer.objects.active = None

    # Get the new object
    new_obj = bpy.context.selected_objects[0]

    # Select only the new object and make it active
    bpy.ops.object.select_all(action='DESELECT')
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = new_obj

    bboxOffset = 0.4

    # Calculate the bounding box of the new object
    min_x = round(new_obj.bound_box[0][0] - bboxOffset, 2)
    max_x = round(new_obj.bound_box[6][0] + bboxOffset, 2)
    min_y = round(new_obj.bound_box[0][1] - bboxOffset, 2)
    max_y = round(new_obj.bound_box[6][1] + bboxOffset, 2)
    min_z = round(new_obj.bound_box[0][2] - bboxOffset, 2)
    max_z = round(new_obj.bound_box[6][2] + bboxOffset, 2)

    # Print the bounding box coordinates
    print("Bounding box:")
    print("  min x:", min_x)
    print("  max x:", max_x)
    print("  min y:", min_y)
    print("  max y:", max_y)
    print("  min z:", min_z)
    print("  max z:", max_z)

    return (min_x, max_x, min_y, max_y, min_z, max_z)

def main():
    print("Executing the main() function in prepUSDZ.py...") # Add this print statement

    # Get the object named "g0"
    geom = bpy.data.objects.get('Geom')
    obj = geom.children[0]    
    ## obj = bpy.data.objects.get("g0")

    # Check if the object exists
    if obj:
        # Unparent and freeze the object
        unparent_object(obj)
        freeze_transforms(obj)
        select_lowest_vertices(0.04)
        select_highest_vertices(0.04)
        select_vertices_near_origin(0.5)
        min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box()
        return (min_x, max_x, min_y, max_y, min_z, max_z)
    else:
        print("Object 'g0' not found in the scene.")

if __name__ == "__main__":
    main()
