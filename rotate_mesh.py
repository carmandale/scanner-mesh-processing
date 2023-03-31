import bpy
import argparse
import os
import shutil

def get_args():
 parser = argparse.ArgumentParser()
 # get all script args
 _, all_arguments = parser.parse_known_args()
 double_dash_index = all_arguments.index('--')
 script_args = all_arguments[double_dash_index + 1: ]

 # add parser rules
 parser.add_argument('-n', '--scan', help="scan name", default = 20220202183126)
 parser.add_argument('-m', '--path', help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") # "/System/Volumes/Data/mnt/scanDrive/takes/") 
 parser.add_argument('-p', '--padding', help="padding", default = 0.0) 
 parsed_script_args, _ = parser.parse_known_args(script_args)
 return parsed_script_args

args = get_args()
scan = str(args.scan)
path = str(args.path)
padding = float(args.padding)

context = bpy.context
ob = context.object
scene = context.scene

def move_and_rename_file(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)

def SelectObject (name):
    ob = scene.objects[name]       
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = ob    
    ob.select_set(True)
    
def SetObjectMode (value):
    ob = context.active_object 
    if ob != None: # can only be done if an object is selected
        bpy.ops.object.mode_set(mode=value)

SelectObject('g0')
bpy.context.view_layer.objects.active = bpy.data.objects['g0']
bpy.data.objects['g0'].rotation_euler[2] = 3.14159
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Move and rename the existing file
old_filepath = os.path.join(path, str(scan), "photogrammetry", str(scan) + ".png")
new_filepath = os.path.join(path, str(scan), "photogrammetry", str(scan) + "-bak.png")
new_blend_filepath = os.path.join(path, str(scan), "photogrammetry", str(scan) + ".blend")
# move_and_rename_file(old_filepath, new_filepath)

# Set the render path
bpy.context.scene.render.filepath = old_filepath

# Render the still frame
bpy.context.scene.camera = bpy.data.objects['Camera']
bpy.ops.render.render(write_still=True)

# Save the file for runShot script
# bpy.ops.wm.save_mainfile()
# Save the Blender file with the new name
bpy.ops.wm.save_mainfile(filepath=new_blend_filepath)

# #render path
# bpy.context.scene.render.filepath = os.path.join(path ,str(scan),"photogrammetry", str(scan) + ".png")

# #ok then... render the still frame
# bpy.context.scene.camera = bpy.data.objects['Camera']
# bpy.ops.render.render(write_still=True)

# # save the file for runShot script
# bpy.ops.wm.save_mainfile()
