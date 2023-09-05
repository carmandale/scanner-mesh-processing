import argparse
import bpy
from os.path import dirname, abspath
import os

def get_args():
  parser = argparse.ArgumentParser()
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--scan', help="scan name")
  parser.add_argument('-m', '--path', help="diretory", default = "/Users/administrator/groove-test/takes/") 
  parser.add_argument('-a', '--shot', help="shot") 
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args
 
args = get_args()
scan = int(args.scan)
path = str(args.path)
shot = str(args.shot)


#clean up your scene ( assumes  armature is in the scene and is named "Armature")
if "Armature" in bpy.data.objects:
    arm = bpy.data.objects['Armature']
    mesh = bpy.data.objects['Armature'].children[0]
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)


#import path
filepath = os.path.join(path,str(scan),"photogrammetry",str(scan)+"-rig.blend")
bpy.ops.wm.append(
    filepath=filepath,
    directory=os.path.join(os.path.join(filepath,"Collection/")),
                filename="rig")
# import_fbx_path = os.path.join(str(path),str(scan),"gj_"+str(scan)+".fbx")
# import_fbx_texture = os.path.join(str(path),str(scan),"photogrammetry","baked_mesh_tex0.png")
#import armature
# bpy.ops.import_scene.fbx(filepath = import_fbx_path)
#rescale armature
bpy.data.objects['Armature'].scale = (1,1,1)

#select your newly imported armature
objects = bpy.context.scene.objects
for obj in objects:
    new_arm = obj.select_set(obj.type == "ARMATURE")
    print(new_arm)

filename = bpy.path.basename(bpy.context.blend_data.filepath)
if "1450" in str(filename):
  print('football is indeed found')
  bpy.data.objects['footballRig'].pose.bones['root'].constraints["Child Of"].target = bpy.data.objects["Armature"]

#create action
bpy.data.objects['Armature'].animation_data_create()
#apply action
bpy.data.objects['Armature'].animation_data.action = bpy.data.actions.get(shot + "-action")

#add_Material + Texture

bpy.data.objects['Armature'].children[0].select_set(True)

#make new material
# mat = bpy.data.materials.new(name="MAT")
# tex = bpy.data.textures.new("diffuse", 'IMAGE')
# bpy.data.objects['Armature'].children[0].data.materials.append(mat)
# mat.use_nodes = True
# bsdf = mat.node_tree.nodes["Principled BSDF"]
# texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
# texImage.image = bpy.data.images.load(import_fbx_texture)
# mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
# bsdf.inputs[9].default_value = 1

#render path
bpy.context.scene.render.filepath = path + str(scan)+ "\\render\\" + shot + "-char.####.png"

#ok then... render the animation please
bpy.ops.render.render(animation=True)

# save the file for runShot script
savepath = os.path.join(path ,str(scan),"photogrammetry",str(scan) + '_' + shot + '.blend')
bpy.ops.wm.save_as_mainfile(filepath=savepath)

#  blender -b ./sh1300/sh1300.blend -P ./runShots.py -- --scan 20211231120650 --shot sh1300
