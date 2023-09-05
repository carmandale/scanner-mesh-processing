import argparse
import bpy, bmesh, math
from math import radians
from math import pi
from mathutils import Vector, Euler, Matrix, Quaternion 
import os

print('_______________________________________')
print('_______________________________________')
print('________________CleanUp________________')
print('________________3.27.23________________')
print('_______________________________________')

# v2.0.1 based on Stripper_v18
# edited by Dale Carman on 02.20.23
# Start with a clean scene
# bpy.ops.wm.read_factory_settings(use_empty=True)


def get_args():
  parser = argparse.ArgumentParser()
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--scan', help="scan name")
  parser.add_argument('-m', '--path', help="directory", default = "/Users/administrator/groove-test/takes/") 
  parser.add_argument('-p', '--padding', help="padding", default = 0.0) 
  parser.add_argument('-f', '--floor_height', help="floor_height", default = 0.016) 
  parser.add_argument('-r', '--facing', help="facing", default = 0.5) 
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()
scan = str(args.scan)
path = str(args.path)
print("this is the PATH: " + path)
padding = float(args.padding)
floor_height = float(args.floor_height)
facing_threshold = float(args.facing) # previous .5

node_environment_imagePath = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr"

#for local testing
#scan = int(20220409212849)   #(20220503122033) 20220523131315 20220523131418 20220409210708 20220409212849
# scan = int(20220210140645)   #(20220503122033) 20220523131315 20220523131418 20220409210708 20220409212849
# path = str("/Users/administrator/groove-test/takes/") # /System/Volumes/Data/mnt/gjc/productions/FCDallas_Scanner_AR_2202/rawFootage/ /Volumes/scanDrive/takes/
#path = str("/Volumes/scanDrive/takes/") # /System/Volumes/Data/mnt/gjc/productions/FCDallas_Scanner_AR_2202/rawFootage/ /Volumes/scanDrive/takes/
# padding = float(0.0)
# floor_height = float(0.016)
# facing_threshold = .5 # previous .5
extrude_distance = 8.0
threshold = 0.0001
lower_threshold = 0.2

material_name = "MAT"
texture_path = os.path.join(path, str(scan), "photogrammetry", "baked_mesh_tex0.png")




#--------------------------------------------------------------    
#---------------------- USEFUL FUNCTIONS ----------------------
#--------------------------------------------------------------

def pack_textures():
    # Pack all the textures
    for image in bpy.data.images:
        if not image.packed_file:
            image.pack()

def create_middle():
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    for obj in bpy.context.selected_objects:
        obj.name = "mid"
    return bpy.data.objects["mid"]

        
def append_camera():
    #STAGE 7 Append Camera
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(1.9455e-16, -1.56002, 0.876177), rotation=(0, 0, 0), scale=(1, 1, 1))
    bpy.data.objects['Camera'].rotation_euler[0] = 1.5708
    bpy.context.object.data.type = 'ORTHO'
    bpy.context.object.data.ortho_scale = 2.3
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    
def import_model():
    #import USD model
    print(os.path.join(path ,str(scan),"photogrammetry","baked_mesh.usda"))
    import_usd_path = os.path.join(path ,str(scan),"photogrammetry","baked_mesh.usda")
    bpy.ops.wm.usd_import(filepath=import_usd_path)

    # Assign the object with the name "g0" to mesh_obj variable
    Geom_obj = bpy.data.objects['Geom']
    mesh_obj = Geom_obj.children[0]
    mesh_obj.name = 'g0'

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = mesh_obj

    max = 0
    print("facing_threshold = ",facing_threshold)
    arm_distance_Threshold = .2

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # save the file for runShot script
    savepath = os.path.join(path ,str(scan),"photogrammetry",str(scan) + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=savepath)

    return mesh_obj


def create_material(material_name, texture_path):
    #STAGE 5: Create Material
    mat = bpy.data.materials.new(name=material_name)
    tex = bpy.data.textures.new("diffuse", 'IMAGE')
    bpy.data.objects['g0'].data.materials.append(mat)
    bpy.ops.object.material_slot_remove(0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(texture_path)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    mat.node_tree.links.new(bsdf.inputs['Emission'], texImage.outputs['Color'])
    bsdf.inputs[9].default_value = 1
    bsdf.inputs[7].default_value = 0
    bsdf.inputs[20].default_value = 0.5

    
def clean_up_detritis():
    # CLEAN UP DETRITIS - THIS CLEANS UP LOOSE BITS OF THE GAME
    context = bpy.context
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    parts = context.selected_objects
    # sort by number of verts (last has most)
    parts.sort(key=lambda o: len(o.data.vertices))
    # print
    for part in parts:
        print(part.name, len(part.data.vertices))
    # pop off the last
    last = parts.pop()
    # remove the rest
    if len(parts) > 0:
        for o in parts:
            bpy.data.objects.remove(o)
            
def select_feet(target):
    for v in bpy.data.objects[target].data.vertices:
        if v.co[2] < 0.03:
            v.select = True
    selectedVerts = [v for v in bpy.data.objects['g0'].data.vertices if v.select]
    
def vert(vert_list):
    x_list =[]
    for x in vert_list:
        x_dist = math.dist(x, mid.location)
        if x_dist < .7: 
            x_list.append(abs(x_dist))
    x_list.sort(key=lambda x_dist: x_dist, reverse=False)
    max_x = x_list[-1]
    max_y = 2
    return max_x, max_y

def set_origin_to_lowest_vertex(padding):
    # Get the z-coordinates of the vertices
    z_coords = [vert.co[2] for vert in bpy.data.objects['g0'].data.vertices if vert.co[2]]
    
    # Sort the z-coordinates in descending order and get the lowest one
    lowest_z = sorted(z_coords, reverse=True)[-1]
    
    # Set the cursor location to the lowest vertex plus the padding
    bpy.context.scene.cursor.location = (0, 0, lowest_z + padding)
    
    # Set the origin of the object to the cursor location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')


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

            
    
def reset_geometry():
    # Remove any detritus from the mesh
    clean_up_detritis()

    # Set the origin of the object to the center of its geometry
    try:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    except RuntimeError as error:
        print(f"Error: {error}")

    # Move the object to the origin
    try:
        bpy.data.objects['g0'].location = (0,0,0)
    except KeyError as error:
        print(f"Error: {error}")

    print("Geometry reset.")

    
def add_bottom_plane(floor_height, padding):
    # Set the origin of the object to the lowest vertex
    bpy.ops.object.mode_set(mode='OBJECT')
    set_origin_to_lowest_vertex(padding)
    bpy.ops.object.location_clear(clear_delta=False)
    
    # Add a plane at the floor height
    plane_size = 11
    plane_location = (0, 0, floor_height)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_plane_add(size=plane_size, enter_editmode=False, align='WORLD', location=plane_location, scale=(1, 1, 1))
 

def reset_floor():
    # STAGE 2 : Get Bottom Plane
    bpy.ops.object.mode_set(mode = 'OBJECT')
#    bpy.ops.object.editmode_toggle() # GOING TO OBJECT
    set_origin_to_lowest_vertex(padding)
    bpy.ops.object.location_clear(clear_delta=False)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(False)
    bpy.ops.object.mode_set(mode = 'OBJECT')


def extract_floor(threshold, extrude_distance):
    # Extrude the selected region downwards
    bpy.ops.mesh.extrude_region_move(
            MESH_OT_extrude_region={
                "use_normal_flip": False,
                "use_dissolve_ortho_edges": False,
                "mirror": False
            },
            TRANSFORM_OT_translate={
                "value": (0, 0, -extrude_distance),
                "orient_axis_ortho": 'X',
                "orient_type": 'NORMAL',
                "orient_matrix": ((0, -1, 0), (1, 0, -0), (0, 0, 1)),
                "orient_matrix_type": 'NORMAL',
                "constraint_axis": (False, False, True),
                "mirror": False,
                "use_proportional_edit": False,
                "proportional_edit_falloff": 'SMOOTH',
                "proportional_size": 3,
                "use_proportional_connected": False,
                "use_proportional_projected": False,
                "snap": False,
                "snap_target": 'CLOSEST',
                "snap_point": (0, 0, 0),
                "snap_align": False,
                "snap_normal": (0, 0, 0),
                "gpencil_strokes": False,
                "cursor_transform": False,
                "texture_space": False,
                "remove_on_cancel": False,
                "view2d_edge_pan": False,
                "release_confirm": False,
                "use_accurate": False,
                "use_automerge_and_split": False
            }
        )
    
    # Select the linked mesh vertices
    bpy.ops.mesh.select_linked(delimit=set())
    
    # Make the normals consistent
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Perform a boolean intersection with the selected mesh and the active object
    bpy.ops.mesh.intersect_boolean(
            operation='DIFFERENCE',
            use_swap=False,
            use_self=False,
            threshold=threshold,
            solver='EXACT'
        )

   
def Step02Prep():
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [vert.co for vert in bm.verts]
    else:
        verts = [vert.co for vert in obj.data.vertices]

    plain_verts = [vert.to_tuple() for vert in verts]
    
    # STAGE 1 : Get buounding Cylinder Subtraction
#    cylscale = vert(verts)[0]
#    bpy.ops.object.editmode_toggle()
#    bpy.ops.mesh.primitive_cylinder_add(enter_editmode=True, align='WORLD', location=(0.0, 0.0, 0.0), scale=(cylscale +.1, 1, 3))
#    bpy.ops.mesh.intersect_boolean(operation='INTERSECT', use_swap=False, use_self=False, threshold=1, solver='EXACT')

    # STAGE 2 : Get Bottom Plane
#    bpy.ops.object.mode_set(mode = 'OBJECT')
#    set_origin_to_lowest_vertex(padding)
#    bpy.ops.object.location_clear(clear_delta=False)
#    bpy.ops.object.mode_set(mode = 'EDIT')
#    bpy.ops.mesh.primitive_plane_add(size=11, enter_editmode=False, align='WORLD', location=(0.0, 0.0, floor_height), scale=(1, 1, 1))

    #STAGE 3 : Mass Subtraction
#    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, -8), "orient_axis_ortho":'X', "orient_type":'NORMAL', "orient_matrix":((0, -1, 0), (1, 0, -0), (0, 0, 1)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":3, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
#    bpy.ops.mesh.select_linked(delimit=set())
#    bpy.ops.mesh.normals_make_consistent(inside=False)
#    bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE', use_swap=False, use_self=False, threshold=.0001, solver='EXACT')

    # MIDSTAGE 4 : Tack on rotation empty
    bpy.ops.object.editmode_toggle()
    verts = [vert.co for vert in obj.data.vertices]
    
    bpy.ops.object.editmode_toggle()
    
#    clean_up_detritis()

def close_mesh_holes(mesh_obj):
    # Switch to Edit mode and select all vertices
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Fill holes in the mesh
    bpy.ops.mesh.fill_holes(sides=100)

    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    
def prepare_for_orientation():
    # Switch to edit mode and select all vertices
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.editmode_toggle()
    
    # Duplicate selected vertices
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects['g0']
    bpy.ops.object.editmode_toggle(True)
    bpy.ops.mesh.select_all(False)
    bpy.ops.object.editmode_toggle(False)
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    
    # Rename duplicated object, select foot vertices, and clean up mesh
    bpy.context.object.name = "g_targus"
    select_feet("g_targus")
    bpy.ops.object.editmode_toggle(True)                                                     
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.select_linked(delimit=set())
    bpy.ops.transform.resize(value=(1, 1, 0))
    bpy.ops.mesh.merge(type='COLLAPSE')
    bpy.ops.mesh.edge_face_add()
    
    # Transform the duplicated mesh
    bpy.ops.transform.translate(value=(-0, 0, -0), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.263331, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.editmode_toggle(False)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.transform.resize(value=(888, 888, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Join the duplicated mesh with the original mesh
    bpy.ops.object.select_pattern(pattern="g_targus", case_sensitive=False, extend=True)
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects['g0']
    bpy.ops.object.join()

def re_orient():
    #RE-ORIENT THE MESH PLEASE
    context = bpy.context
    ob = context.object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    objs = set(o for o in context.selected_objects if o.type == 'MESH')

    bm = bmesh.new()
    mw = None

    for ob in objs:
        me = ob.data
        bm.from_mesh(me)
        le = sorted(bm.edges, key=lambda e: e.calc_length()).pop()
        axis = (le.verts[1].co - le.verts[0].co).normalized()
        q = axis.rotation_difference(Vector((1, 0, 0)))
        R = q.to_matrix()
        if ob == context.object:
            mw = R.to_4x4().inverted() 
        me.transform(R.to_4x4())
        bm.clear()

    for o in (o for o in context.selected_objects if o.type == 'MESH'):
        o.matrix_world @= mw

    bpy.ops.object.editmode_toggle(True)
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.editmode_toggle(False)
    bpy.ops.object.rotation_clear(clear_delta=False)
    
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects['g0']

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    center_of_mass = bpy.data.objects['g0'].location
    #bpy.ops.object.location_clear(clear_delta=False)
    bpy.context.scene.cursor.location = Vector((center_of_mass[0],center_of_mass[1],0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')

    bpy.data.objects['g0'].location = (0,0,0)
    bpy.ops.object.select_all(action='DESELECT')

def select_lower_chunk(mesh_obj, lower_threshold):
    for v in mesh_obj.data.vertices:
        if v.co[2] < lower_threshold:
            v.select = True
    selectedVerts = [v for v in mesh_obj.data.vertices if v.select]
    n = len(selectedVerts)
    assert(n)
    between_the_feet = (sum([o.co for o in selectedVerts], Vector())/n) + Vector((0,0,0))
    bpy.context.scene.cursor.location = Vector((center_of_mass[0], center_of_mass[1], between_the_feet[2]))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
    bpy.ops.object.location_clear(clear_delta=False)

    
def check_front_back_facing(mesh_obj, lower_threshold, facing_threshold):
    # Select the lower chunk of the mesh
    select_lower_chunk(mesh_obj, lower_threshold)
    
    # Calculate between-the-feet vector
    selected_verts = [v for v in mesh_obj.data.vertices if v.select and v.co[2] < lower_threshold]
    between_the_feet = sum([v.co for v in selected_verts], Vector()) / len(selected_verts)

    # Check front/back facing
    y_list = [v.co for v in selected_verts if v.co[1] > between_the_feet[1]]
    if len(selected_verts) * facing_threshold > len(y_list):
        print('Model is facing back, rotating...')
        mesh_obj.rotation_euler[2] = 3.14159
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    else:
        print("Model is facing front, seems to check out")

def move_foot_verts():
    # Select the g0 object
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
    bpy.context.view_layer.objects.active = bpy.data.objects['g0']

    ob = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()

    # Move the selected vertices to 0
    for v in bm.verts:
        if v.co[2] < floor_height + 0.00001:
            v.co[2] = 0.0

    bm.to_mesh(ob.data)
    ob.data.update()

def remove_doubles(mesh_obj):
    # Check if the passed object is a mesh
    if mesh_obj.type != 'MESH':
        print(f"Object '{mesh_obj.name}' is not a mesh.")
        return

    # Check if the object is in Edit mode
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    # Get a BMesh representation of the mesh
    bm = bmesh.from_edit_mesh(mesh_obj.data)

    # Remove doubles from the mesh
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    # Update the mesh with the modified BMesh
    bmesh.update_edit_mesh(mesh_obj.data)

    # Cleanup
    bm.free()

    # Toggle back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    
def move_to_collection(obj, collection_name):
    # Get the collection to move the object to
    collection = bpy.data.collections.get(collection_name)
    
    # If the collection doesn't exist, create it and link it to the scene
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        print(f"Collection '{collection_name}' created.")

    # Move the object to the collection
    obj_collection = obj.users_collection[0]
    obj_collection.objects.unlink(obj)
    collection.objects.link(obj)

   
def render_and_save(obj_name, camera_name, output_path):
    # Set the object location to (0, 0, 0)
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print(f"Object '{obj_name}' not found.")
        return
    obj.location = (0, 0, 0)

    # Set the output file path
    bpy.context.scene.render.filepath = os.path.join(output_path, "photogrammetry", f"{scan}.png")

    # Set the active camera
    camera = bpy.data.objects.get(camera_name)
    if camera is None:
        print(f"Camera '{camera_name}' not found.")
        return
    bpy.context.scene.camera = camera

    # Render the still frame
    result = bpy.ops.render.render(write_still=True)

    # Save the file
    bpy.ops.wm.save_mainfile()

    # Check if the render operation was successful
    if result != {'FINISHED'}:
        print("Render failed.")


    
def add_hdr():
    C = bpy.context
    scn = C.scene

    # Get the environment node tree of the current scene
    node_tree = scn.world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(node_environment_imagePath) # Relative path
    node_environment.location = -300,0

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 200,0

    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

# import the model, set the material and the camera
create_middle()
append_camera()
add_hdr()
mesh_obj = import_model()
create_material(material_name, texture_path)

add_bottom_plane(floor_height, padding)
extract_floor(threshold, extrude_distance)
move_foot_verts()

reset_geometry() # Clean up and center to center of mass
reset_floor()
###Step02Prep() # Put feet on floor_height and clean ground

prepare_for_orientation() # add the rotation line

re_orient()

center_of_mass = bpy.data.objects['g0'].location

check_front_back_facing(mesh_obj, lower_threshold, facing_threshold)

remove_doubles(mesh_obj)
close_mesh_holes(mesh_obj)


move_to_collection(mesh_obj, "geo")

obj_name = "g0"
camera_name = "Camera"
output_path = os.path.join(path, str(scan))

pack_textures()

render_and_save(obj_name, camera_name, output_path)





