import bpy
import argparse
import os

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

#scan = 20220202183126
#path = "/System/Volumes/Data/mnt/scanDrive/takes/"

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

# bpy.ops.object.editmode_toggle()
# bpy.ops.object.select_all(action='DESELECT')
# bpy.ops.object.select_pattern(pattern="g0", case_sensitive=False, extend=True)
# bpy.context.view_layer.objects.active = bpy.data.objects['g0']


# bpy.ops.object.editmode_toggle()
# bpy.ops.mesh.select_all(action='SELECT')
# bpy.ops.transform.rotate(value=3.14159, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.263331, use_proportional_connected=False, use_proportional_projected=False)
# bpy.ops.object.editmode_toggle()

#render path
bpy.context.scene.render.filepath = os.path.join(path ,str(scan),"photogrammetry", str(scan) + ".png")

#ok then... render the still frame
bpy.context.scene.camera = bpy.data.objects['Camera']
bpy.ops.render.render(write_still=True)

# save the file for runShot script
bpy.ops.wm.save_mainfile()
