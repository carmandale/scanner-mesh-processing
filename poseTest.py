import bpy
import os
import sys

argv = sys.argv
input_file = argv[argv.index('--') + 1]

# Open the input file
bpy.ops.wm.open_mainfile(filepath=input_file)

# Function to append a camera
def append_camera():
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(1.9455e-16, -1.56002, 0.876177), rotation=(0, 0, 0), scale=(1, 1, 1))
    camera = bpy.context.active_object
    bpy.data.objects['Camera'].rotation_euler[0] = 1.5708
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2.3
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920

    # Set the added camera as the active camera for the scene
    bpy.context.scene.camera = camera

# Function to select an Armature object
def select_armature_object():
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            return obj
    return None

# Function to pose the specified bones
def pose_bones(armature_obj, bone_names):
    if armature_obj is None:
        return

    bpy.ops.object.mode_set(mode='POSE')

    for bone_name in bone_names:
        if bone_name in armature_obj.pose.bones:
            bone = armature_obj.pose.bones[bone_name]
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler = (5.5, 0, 0)

    bpy.ops.object.mode_set(mode='OBJECT')

# Select the armature object
armature = select_armature_object()

# Pose the specific bones
bone_names = ['mixamorig:RightArm', 'mixamorig:LeftArm', 'mixamorig:RightLeg', 'mixamorig:LeftLeg', 'mixamorig:Spine']
pose_bones(armature, bone_names)

# Append the camera
append_camera()

# Set the output file path and render the image
blend_file_path = bpy.data.filepath
output_directory = os.path.dirname(blend_file_path)
output_filename = "pose-test.png"
output_filepath = os.path.join(output_directory, output_filename)

bpy.context.scene.render.filepath = output_filepath
bpy.ops.render.render(write_still=True)

# Save the blend file with the "-poseTest" suffix
input_directory, input_filename = os.path.split(input_file)
input_name, input_extension = os.path.splitext(input_filename)
output_file = f"{input_name}-poseTest{input_extension}"
output_path = os.path.join(input_directory, output_file)

bpy.ops.wm.save_as_mainfile(filepath=output_path)

