#!/bin/sh

# create the photogrammetry directory if it does not exist
mkdir -p /Users/administrator/groove-test/takes/$1/photogrammetry

#process the scan
echo "-----------------------"
echo "-----------------------"
echo "-----------------------"
echo "Processing the scan ..."
echo "-----------------------"
echo "-----------------------"
echo "-----------------------"
/Users/groovejones/scene_machine/sequence/utility/groove-mesher2022-01-06-12-33-17/groove-mesher /Users/administrator/groove-test/takes/$1/source /Users/administrator/groove-test/takes/$1/photogrammetry/ -d full 

#cleanup the model
echo "------------------------"
echo "------------------------"
echo "------------------------"
echo "Cleaning up the scan ..."
echo "------------------------"
echo "------------------------"
echo "------------------------"
#/Applications/Blender.app/Contents/MacOS/Blender -b /Users/administrator/groove-test/software/2.10.22_updates/retarget/cleanup_v14.blend -P /Users/administrator/groove-test/software/2.10.22_updates/retarget/stripper_v18.py -- --scan $1 

#run pose detection
echo "--------------------------"
echo "--------------------------"
echo "--------------------------"
echo "Running pose detection ..."
echo "--------------------------"
echo "--------------------------"
echo "--------------------------"
#python /Users/groovejones/Software/pose_gen_package/pose_generator.py -i /Users/administrator/groove-test/takes/$1/photogrammetry/$1.png -o /Users/administrator/groove-test/takes/$1/photogrammetry/$1_results.txt
