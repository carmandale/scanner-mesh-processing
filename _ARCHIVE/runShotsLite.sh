#!/bin/sh

# create the photogrammetry directory if it does not exist
mkdir -p /Volumes/scanDrive/takes/$1/photogrammetry

#process the scan
echo "-----------------------"
echo "-----------------------"
echo "-----------------------"
echo "Processing the scan ..."
echo "-----------------------"
echo "-----------------------"
echo "-----------------------"
#/Users/groovejones/scene_machine/sequence/utility/groove-mesher2022-01-06-12-33-17/groove-mesher /Volumes/scanDrive/takes/$1/source /Volumes/scanDrive/takes/$1/photogrammetry/ -d full 

#cleanup the model
echo "------------------------"
echo "------------------------"
echo "------------------------"
echo "Cleaning up the scan ..."
echo "------------------------"
echo "------------------------"
echo "------------------------"
#/Applications/Blender.app/Contents/MacOS/Blender -b /Volumes/scanDrive/software/2.10.22_updates/retarget/cleanup_v14.blend -P /Volumes/scanDrive/software/2.10.22_updates/retarget/stripper_v18.py -- --scan $1 --floor 0.0045

# rotate the model
# echo /Applications/Blender.app/Contents/MacOS/Blender -b /Volumes/scanDrive/takes/$1/photogrammetry/$1.blend   -P /Volumes/scanDrive/software/2.10.22_updates/retarget/rotate_mesh.py -- --scan $1
#/Applications/Blender.app/Contents/MacOS/Blender -b /Volumes/scanDrive/takes/$1/photogrammetry/$1.blend   -P /Volumes/scanDrive/software/2.10.22_updates/retarget/rotate_mesh.py -- --scan $1



#run pose detection
echo "--------------------------"
echo "--------------------------"
echo "--------------------------"
echo "Running pose detection ..."
echo "--------------------------"
echo "--------------------------"
echo "--------------------------"
python /Users/groovejones/Software/pose_gen_package/pose_generator.py -i /Volumes/scanDrive/takes/$1/photogrammetry/$1.png -o /Volumes/scanDrive/takes/$1/photogrammetry/$1_results.txt

#rig the model
echo "---------------------"
echo "---------------------"
echo "---------------------"
echo "Rigging the model ..."
echo "---------------------"
echo "---------------------"
echo "---------------------"
# echo /Applications/Blender.app/Contents/MacOS/Blender -b -P /Volumes/scanDrive/software/2.10.22_updates/retarget/AddRig.py -- --scan $1
/Applications/Blender.app/Contents/MacOS/Blender -b -P /Volumes/scanDrive/software/2.10.22_updates/retarget/AddRig.py -- --scan $1

# run the shots
echo "-------------------------"
echo "-------------------------"
echo "-------------------------"
echo "Retargeting the model ..."
echo "-------------------------"
echo "-------------------------"
echo "-------------------------"
echo /Volumes/scanDrive/software/2.10.22_updates/retarget/retargetScan.sh $1
echo "-------------------------"
/Volumes/scanDrive/software/2.10.22_updates/retarget/retargetScan.sh $1

# run the shots
echo "-------------------------"
echo "-------------------------"
echo "-------------------------"
echo "Optimizing the models ..."
echo "-------------------------"
echo "-------------------------"
echo "-------------------------"
echo /Volumes/scanDrive/software/2.10.22_updates/retarget/transform-glbs.sh $1
echo "-------------------------"
/Volumes/scanDrive/software/2.10.22_updates/retarget/transform-glbs.sh $1

