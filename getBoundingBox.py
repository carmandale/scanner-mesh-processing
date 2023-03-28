import bpy
import bmesh
from mathutils import Vector

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

# Calculate the bounding box of the new object
min_x = new_obj.bound_box[0][0]
max_x = new_obj.bound_box[6][0]
min_y = new_obj.bound_box[0][1]
max_y = new_obj.bound_box[6][1]
min_z = new_obj.bound_box[0][2]
max_z = new_obj.bound_box[6][2]

# Print the bounding box coordinates
print("Bounding box:")
print("  min x:", min_x)
print("  max x:", max_x)
print("  min y:", min_y)
print("  max y:", max_y)
print("  min z:", min_z)
print("  max z:", max_z)