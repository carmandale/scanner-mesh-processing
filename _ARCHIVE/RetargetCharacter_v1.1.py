import argparse
import bpy
import math
import os
import numpy as np
import sys
import time
from mathutils import Euler

context = bpy.context
ob = context.object
scene = context.scene

# v1.1

def get_args():
  parser = argparse.ArgumentParser()
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--scan', help="scan name")
  parser.add_argument('-m', '--path', help="directory", default = "/Volumes/scanDrive2/takes/") 
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args 

args = get_args()
scan = int(args.scan)
scanID = str(scan)
path = str(args.path)

#--------------------------------------------------------------    
#----------------------- MAIN GLOBAL VARIABLES ----------------
#--------------------------------------------------------------

time_start = time.time()
canRun = True
shouldRender = True

#--------------------------------------------------------------    
#--------------------- APPEND SCANNED CHARACTERS --------------
#--------------------------------------------------------------
print ("\n- Append scan character: START -\n")

def appendScan(filepath):

    directory = os.path.join(os.path.join(filepath, "Collection/"))
    filename = "rig"
    
    print ('-- Attempting to append the filename: "%s" from the directory: %s \n' %(filename, directory))
    
    bpy.ops.wm.append(
        filepath=filepath,
        directory=directory,
        filename=filename)
    
    if scene.objects.get("Armature") != None:
        return print("- Append scan character: FINISHED Succesfully -\n")   
            
scan_blend_file_path = path
scan_blend_file_name = scanID + '-rig.blend'

finalPath = os.path.join(scan_blend_file_path, scanID, "photogrammetry", scan_blend_file_name)

try:
    appendScan(finalPath) 
except:
    canRun = False
    print('ERROR: %s not found! ' % (finalPath))   

#--------------------------------------------------------------    
#---------------------- USEFUL FUNCTIONS ----------------------
#--------------------------------------------------------------

def SetFrame (value):
    bpy.context.scene.frame_set(value)
    return print("-- Frame set to: %s" %(value))
    
def GetActionLength (name):    
    ac = bpy.data.actions.get(name)
       
    firstFrame = 9999999
    lastFrame = -9999999
    
    for fc in ac.fcurves:
        for p in fc.keyframe_points:
            x, y = p.co
            k = math.ceil(x)
            
            if k < firstFrame:
                firstFrame = k
                
            if k > lastFrame:
                lastFrame = k                
    return [firstFrame, lastFrame]
    
def SelectObject (name):
    ob = scene.objects[name]       
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = ob    
    ob.select_set(True)
    
def SetObjectMode (value):
    ob = context.active_object 
    if ob != None: # can only be done if an object is selected
        bpy.ops.object.mode_set(mode=value)

def FindChild (parentObj, childName):
    if parentObj == None:
        return
    for c in parentObj.children:
        if c.name == childName:
            return c
        
def FindObjectsWithPrefix(prefix):
    objs = []
    for obj in scene.objects:
        if obj.name.startswith(prefix):
            objs.append(obj)
    return objs
        
def SelectAndSetAsActive (obj):
    if obj == None:
        return
    obj.select_set(True)
    context.view_layer.objects.active = obj
    
# GEOMETRY_ORIGIN, ORIGIN_GEOMETRY, ORIGIN_CURSOR, ORIGIN_CENTER_OF_MASS, ORIGIN_CENTER_OF_VOLUME 
def SetObjOrigin (obj, type = 'ORIGIN_GEOMETRY', center = 'MEDIAN'):
    if obj == None:
        return
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type=type,center=center)
    
def CreateEmptyOnObjectLocation (obj, radius=0.1, name='Empty', type='ARROWS', useWorld=True):
    target = obj
    if target == None:
        return
    
    loc = target.location
    if useWorld == True:
        loc = target.matrix_world.translation        
    
    newEmpty = bpy.ops.object.empty_add(radius=radius, type=type, location=loc)
    context.active_object.name = name
    return context.active_object

def GetOrCreateCollection (scene, collection_name):
    collection = bpy.data.collections.get( collection_name )
    if collection is None:
        collection = bpy.data.collections.new( collection_name )
        scene.collection.children.link( collection )
    return collection

def SetToCollection (obj, collection):
    if obj == None:
        return
    collection.objects.link(obj)
    
def RemoveFromAllCollections(obj):
    if obj == None:
        return
    for col in obj.users_collection:
        col.objects.unlink(obj)
        return obj
        
# CLEAR, CLEAR_KEEP_TRANSFORM, CLEAR_INVERSE
def ClearParent (obj, type='CLEAR_KEEP_TRANSFORM'):
    if obj == None:
        return
    context.view_layer.objects.active = obj
    bpy.ops.object.parent_clear(type=type)
    
def ApplyModifier(obj, modifierName):
    if obj == None:
        return
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifierName)

def SetCursorToObjectLocation(obj, useWorld=True):
    if obj == None:
        return
    loc = obj.location
    if useWorld == True:
        loc = obj.matrix_world.translation 
    scene.cursor.location = loc

def RemoveObj(obj, do_unlink=True):
    bpy.data.objects.remove(obj, do_unlink=do_unlink)

def RemoveParentAndChildren (parent, do_unlink=True):
    print('------------- ATTEMPTING TO REMOVE -------------')
    print(parent.name)
    if len(parent.children) > 0:
        for c in parent.children:
            bpy.data.objects.remove(c, do_unlink=do_unlink)
    bpy.data.objects.remove(parent, do_unlink=do_unlink)

def SetObjectScale (obj, value):
    obj.scale = value
    
def ApplyTransform(obj, location=True, rotation=True, scale=True, properties=True):
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = obj    
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale, properties=properties)
    
def SetCameraLensAtFrame(camName, lens, frame):
    cam = scene.objects.get(camName)
    if cam == None:
        return print ("-- %s not found!" %(camName))

# RENDERING

def SetSceneFrameRange(startFrame, endFrame):
    scene.frame_start = startFrame
    scene.frame_end = endFrame
    return print ('-- Scene Frame Range set to: S:' + str(startFrame) + ' | E:' + str(endFrame))

def SetRenderFileFormatToPNG(useAlpha = True, is16BIT = False, compression = 0):
    scene.render.image_settings.file_format = 'PNG'
    
    colorMode = 'RGB'
    colorDepth = '8'
    
    if useAlpha == True:
        colorMode = 'RGBA'    
    
    if is16BIT == True:
        colorDepth = '16'
        
    scene.render.image_settings.color_mode = colorMode    
    scene.render.image_settings.color_depth = colorDepth        
    scene.render.image_settings.compression = compression           
    
    return print ("Render File Format set to PNG-%s-%sbit | compression: %s" %(colorMode, colorDepth, compression))

def SetRenderFilePath(folderPath, fileName):    
    filePath = folderPath + fileName
    scene.render.filepath = filePath
    return print ('Render File Path set to: ' + filePath)

def SetRenderFPS(value):
    scene.render.fps = value
    return print ('Render FPS set to: ' + str(value))

def RenderSceneAnimation():
    bpy.ops.render.render(animation=True)
    startFrame = str(scene.frame_start)
    endFrame = str(scene.frame_end)
    fileFormat = scene.render.image_settings.file_format
    fps = str(scene.render.fps)    
    return print ("- Rendered PNG sequence from frame:%s to frame:%s -" % (startFrame, endFrame)) 
   
SetFrame(1)

#-------------------------------------------------------------    
#------------------------- VARIABLES -------------------------
#-------------------------------------------------------------

source = scene.objects.get("scanChar-rig")
target = scene.objects.get("Armature")

targetModel = target.children[0]

sourceHips = source.pose.bones.get("mixamorig:Hips")
targetHips = target.pose.bones.get("mixamorig:Hips")

toeR = target.pose.bones.get("mixamorig:RightToeBase")
toeL = target.pose.bones.get("mixamorig:LeftToeBase")
head = target.pose.bones.get('mixamorig:Head')
neck = target.pose.bones.get('mixamorig:Neck')
spine2 = target.pose.bones.get('mixamorig:Spine2')
handLeft = target.pose.bones.get('mixamorig:LeftHand')

bonesToRetarget = []
bonesToRetargetNames = [
"mixamorig:RightArm", "mixamorig:LeftArm", "mixamorig:RightForeArm",
"mixamorig:LeftForeArm", "mixamorig:RightHand", "mixamorig:LeftHand",
"mixamorig:LeftShoulder", "mixamorig:RightShoulder", "mixamorig:RightUpLeg",
"mixamorig:RightLeg", "mixamorig:LeftUpLeg", "mixamorig:LeftLeg"]

for n in range(0, len(bonesToRetargetNames)):
    bonesToRetarget.append(target.pose.bones.get(bonesToRetargetNames[n])) 

# Target Parent 
   
targetParent = scene.objects.get("scanCharParent")
target.parent = targetParent

# Camera Variables
'''
cam11 = scene.objects.get("cam11")
cam11Target = scene.objects.get("cam11-target")

cam12 = scene.objects.get("cam12")
cam12Target = scene.objects.get("cam12-target")

cam13Target = scene.objects.get("cam13-target")

cam14 = scene.objects.get("cam14")
cam14Target = scene.objects.get("cam14-target")
'''

'''
if not all([source, target, sourceHips, targetHips, toeR, toeL, head, neck, spine2, handLeft, targetParent, headBallPointParent,
leftBallPointParent, rightBallPointParent, leftBallPointCam0, rightBallPointCam0, snapPointCam0, leftBallPointCam1_f63,
leftBallPointCam1_f64, ballPointCam9, cam11, cam11Target, cam12, cam12Target, cam13Target, cam14, cam14Target ] + bonesToRetarget):
    canRun = False
    print ("\n- ERROR: Something is missing either from the scan character or the scene -\n")
'''

if not all([source, target, sourceHips, targetHips, toeR, toeL, head, neck, spine2, handLeft, targetParent] + bonesToRetarget):
    canRun = False
    print ("\n- ERROR: Something is missing either from the scan character or the scene -\n")    
# Render Variables

renderFrames = [
[31,96], #Cam sh2000
[97,124], #Cam sh3000
[125,166], #Cam sh4000
[167,196], #Cam sh5000
[283,309], #Cam sh8000
[310,336], #Cam sh9000
[337,409], #Cam sh10000
[410,480]] #Cam sh11000

#--------------------------------------------------------------    
#--------------------------- ACTIONS --------------------------
#--------------------------------------------------------------

def SetActions():
    print ("\n- Setting actions: START -\n")

    parentAction = bpy.data.actions.get("scanCharParent-action").copy()
    targetParent.animation_data.action = parentAction

    actionName = "ScanChar-Action-v13-BakedToBones"
    targetAction = bpy.data.actions.get(actionName).copy()
    
    visibilityActionName = "scanChar-model-Action"
    targetVisibilityAction = bpy.data.actions.get(visibilityActionName).copy()

    if target.animation_data != None:
        target.animation_data.action = targetAction    
    else:
        target.animation_data_create()
        target.animation_data.action = targetAction
        
    if targetModel.animation_data != None:
        targetModel.animation_data.action = targetVisibilityAction    
    else:
        targetModel.animation_data_create()
        targetModel.animation_data.action = targetVisibilityAction    
        

    print ("-- Parent action: %s | scanChar action: %s" %(parentAction.name, targetAction.name))

    return print ("\n- Setting actions: FINISHED -")
    
#----------------------------------------------------------------    
#------------------ SET CHARACTER WORLD MATRIX ------------------
#----------------------------------------------------------------

def SetCharacterMatrix():
    print ("\n- Setting character world matrix: START -\n")

    obj = targetHips.id_data
    obj2 = sourceHips.id_data

    obj.matrix_world = obj2.matrix_world

    print ("-- scanChar new matrix: %s" %(obj2.matrix_world))

    return print ("\n- Setting character world matrix: FINISHED -")

#---------------------------------------------------------------    
#---------------- RETARGET CHARACTER BODY PARTS ----------------
#---------------------------------------------------------------

def RetargetBones(bonesArray):
    print ("\n- Retarget Body Parts: START -\n")
    
    for b in bonesArray:
        constraints = [c for c in b.constraints]        
        for c in constraints:
            b.constraints.remove (c)
        newCopyRot = b.constraints.new('COPY_ROTATION')
        newCopyRot.name = 'rot'
        newCopyRot.target = source
        newCopyRot.subtarget = b.name
        print ("-- %s constraint: %s | target: %s | subtarget: %s"  % (b.name, 'rot', source.name, b.name ))
    
    return print ("\n- Retarget Body Parts: FINISHED -")
    
#---------------------------------------------------------------    
#------------------------ RETARGET FEET ------------------------
#---------------------------------------------------------------

def RetargetFeet():
    print ("\n- Retarget Feet: START -\n")
    
    for i in range (17, 501):
        bpy.context.scene.frame_set(i)
        toeR_Tail_Loc = target.location + toeR.tail
        toeL_Tail_Loc = target.location + toeL.tail
        minLocZ = min(toeR_Tail_Loc.z,toeL_Tail_Loc.z) # find the lowest value
        if minLocZ < 0:
            #print ("f:" + str(i) + " " + str(minLocZ))
            SetFrame(i)
            print ("-- Hips offset +%s" % (abs(minLocZ)))
            targetParent.location = (0,0, abs(minLocZ))
            targetParent.keyframe_insert(data_path="location", frame = i)

    return print ("\n- Retarget Feet: FINISHED -")    

#--------------------------------------------------------------    
#------------------------- FIX CAMERAS ------------------------
#--------------------------------------------------------------
def FixCam11():
    print ("\n- Fix Camera 11: START -\n")
    
    objs = [cam11, cam11Target]
    
    camThresholdMin = 0.30
    camThresholdMax = 0.45    
    
    print ("-- Cam min threshold: %s" %(camThresholdMin))
    print ("-- Cam max threshold: %s" %(camThresholdMax))
    
    frameStart = 360
    frameEnd = 394
    
    SetFrame(frameStart)
    
    neckLocation = target.location + neck.tail
    handLocation = target.location + handLeft.head 
    
    distFromHeadToHand = neckLocation[0] - handLocation[0]
    
    focalLengthAtStart = 200
    focalLengthAtEnd = 150
    
    offset = 0
    offsetIfFar = 0.1
    OffsetIfClose = 0.05
    
    # TODO: Add an extra threshold to increase the focal length 
    # more when the character is quite small
    
    if distFromHeadToHand >= camThresholdMax:
        offset = offsetIfFar
        focalLengthAtStart = 200
        focalLengthAtEnd = 150
        print ("-- distFromHeadToHand > camThreshold: %.2f" %(distFromHeadToHand))
        print ("-- Using far offset: %s" %(offset))
    else:
        offset = OffsetIfClose
        focalLengthAtStart = 200
        focalLengthAtEnd = 150
        print ("-- camThreshold > distFromHeadToHand: %.2f" %(distFromHeadToHand))
        print ("-- Using close offset: %s" %(offset))
        
    SetCameraLensAtFrame(camName = 'cam11', lens = focalLengthAtStart, frame = frameStart)  
    
    for obj in objs:
        obj.location[2] = neckLocation[2] + offset
        obj.keyframe_insert(data_path="location", frame = frameStart)     
    
    print ("-- Cam 11 height set to neck height + offset: %.2f" %(cam11.location[2]))
    
    SetFrame(frameEnd) 
    
    neckLocation = target.location + neck.tail
    
    SetCameraLensAtFrame(camName = 'cam11', lens = focalLengthAtEnd, frame = frameEnd) 
    
    for obj in objs:
        obj.location[2] = neckLocation[2] + offset
        obj.keyframe_insert(data_path="location", frame = frameEnd)
        
    print ("-- Cam 11 height set to neck height + offset: %.2f" %(cam11.location[2]))
    
    return print ("\n- Fix Camera 11 Location: FINISHED -")

def FixCam12():
    print ("\n- Fix Camera 12: START -")
 
    frameStart = 450
    frameEnd = 464
    
    SetFrame(frameStart)     
    
    spine2Location = target.location + spine2.head # + targetParent.location
    
    cam12.location[2] = spine2Location[2]
    cam12.keyframe_insert(data_path="location", frame = frameStart)
    print ("-- Camera height set to: %s" %(spine2Location[2]))
    
    SetFrame(frameEnd)     
    
    spine2Location = target.location + spine2.head # + targetParent.location    
    
    cam12.location[2] = spine2Location[2]
    cam12.keyframe_insert(data_path="location", frame = frameEnd)
    print ("-- Camera height set to: %s" %(spine2Location[2]))

    return print ("\n- Fix Camera 12: FINISHED -") 

def FixCam13():
    print ("\n- Fix Camera 13: START -\n")
   
    frameStart = 482
    frameEnd = 500
    
    SetFrame(frameStart)     
    
    headLocation = target.location + head.tail # + targetParent.location  
    
    cam13Target.location[2] = headLocation[2]
    cam13Target.keyframe_insert(data_path="location", frame = frameStart)
    print ("-- Camera height set to: %s" %(headLocation[2]))
    
    SetFrame(frameEnd)     
    
    headLocation = target.location + head.tail # + targetParent.location   
    
    cam13Target.location[2] = headLocation[2]
    cam13Target.keyframe_insert(data_path="location", frame = frameEnd)
    print ("-- Camera height set to: %s" %(headLocation[2]))

    return print ("\n- Fix Camera 13: FINISHED -")

def FixCam14():
    print ("\n- Fix Camera 14: START -\n")
    
    objs = [cam14, cam14Target]    
    frameEnd = 545
    
    SetFrame(frameEnd)    
    
    headLocation = target.location + head.tail # + targetParent.location    
    headHeight = headLocation[2] 
    
    camHeight = 0
    
    if headHeight >= 1.80:
        print ("-- Character head height: %.2f >= %s" %(headHeight, 1.80))
        camHeight = 1.70                        
    
    if headHeight >= 1.60 and headHeight < 1.80:
        print ("-- Character head height: %.2f >= %s and < %s" %(headHeight, 1.60, 1.80))
        camHeight = 1.40              
    
    if headHeight >= 1.25 and headHeight < 1.60:
        print ("-- Character head height: %.2f > %s and < %s" %(headHeight, 1.25, 1.60))
        camHeight = 1.05
         
    if headHeight < 1.25:
        print ("-- Character head height: %.2f < %s" %(headHeight, 1.25))
        camHeight = 0.65               
    
    cam14.location[2] = camHeight
    cam14.keyframe_insert(data_path="location", frame = frameEnd)
    print ("-- Camera height set to: %s" %(camHeight))
    
    return print ("\n- Fix Camera 14: FINISHED -\n") 

def SetRenderFileFormatToJPG(quality = 50):
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = quality
    return print ("Render File Format set to JPEG | Quality: %s" % (quality))

#--------------------------------------------------------------    
#---------------------------- MAIN ----------------------------
#--------------------------------------------------------------

def main():
    
    SetActions()
    
    SetCharacterMatrix()
    RetargetBones (bonesToRetarget)    
    #RetargetFeet()
    
    #FixCam11()
    #FixCam12()
    #FixCam13()
    #FixCam14()    

    if shouldRender == True:    
        SetRenderFileFormatToPNG(is16BIT = False, compression = 0)
        SetRenderFilePath(path + scanID + "\\render\\", "scan" + '.####.png')    
        SetRenderFPS(24)
        
        # Render specific frames
        for frames in renderFrames:
            SetSceneFrameRange(frames[0], frames[1])
            RenderSceneAnimation()   

        # Render thumbnail frame
        # SetRenderFileFormatToJPG(quality = 50)
        # SetRenderFilePath(path + scanID + "\\render\\", "scan" + '-thumbnail.jpg')
        # SetSceneFrameRange(466, 466)
        # RenderSceneAnimation()      
     
    s = time.time() - time_start
    m = s/60   
    return print("\n- Total elapsed time: %.2f min | %.2f sec -" % (m, s))

if canRun == True:
    main()
