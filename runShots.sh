#!/bin/sh

software="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/Software/02.20.23"
blender="/Applications/Blender.app/Contents/MacOS/Blender"
posegen="/Users/groovejones/Software/pose_gen_package/pose_generator.py"
faceDetect="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/Software/scannermeshprocessing-2023/pose_gen_package/face_detector.py"

# Check if the second command line argument is provided
if [ -z "$2" ]; then
  # If the second argument is not provided, use a predefined default path
#   base_path="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/CFP_sample_data"
#   base_path="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/problemScansNBA"
  base_path="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/CFP_problem_scans"
else
  # If the second argument is provided, use it as the base path
  base_path="$2"
fi

# create the photogrammetry directory if it does not exist
# mkdir -p /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry

#process the scan
# echo "-----------------------"
# echo "-----------------------"
# echo "-----------------------"
# echo "Processing the scan ..."
# echo "-----------------------"
# echo "-----------------------"
# echo "-----------------------"
# /System/Volumes/Data/mnt/scanDrive/software/5.2.22/groove-mesher2022-01-06-12-33-17/groove-mesher /System/Volumes/Data/mnt/scanDrive/takes/$1/source /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/ -d full
# /Users/dalecarman/Library/Developer/Xcode/DerivedData/groove-mesher-evwsmvlvqzrhocgwvhxppciaqigu/Build/Products/Debug/groove-mesher /System/Volumes/Data/mnt/scanDrive/takes/$1/source /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/ -d full
"$software/generateMesh.sh" $1 "$base_path"

#cleanup the model
echo "------------------------"
echo "------------------------"
echo "------------------------"
echo "Cleaning up the scan ..."
echo "------------------------"
echo "------------------------"
echo "------------------------"
#  /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/software/5.2.22/cleanup_v14.blend -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/stripper_v18.py -- --scan $1 --floor 0.2145
# /Applications/Blender.app/Contents/MacOS/Blender -b -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/CleanUp.py  -- --scan $1 --facing 0.5 --path $2
"$blender" -b -P "$software/CleanUp.py"  -- --scan $1 --facing 0.5 --path "$base_path"

# rotate the model
# echo /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/$1.blend   -P /System/Volumes/Data/mnt/scanDrive/software/2.10.22_updates/retarget/rotate_mesh.py -- --scan $1
# /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/$1.blend   -P /System/Volumes/Data/mnt/scanDrive/software/2.10.22_updates/retarget/rotate_mesh.py -- --scan $1

#run pose detection
# echo "--------------------------"
# echo "--------------------------"
# echo "--------------------------"
# echo "Running pose detection ..."
# echo "--------------------------"
# echo "--------------------------"
# echo "--------------------------"
# python /Users/groovejones/Software/pose_gen_package/pose_generator.py -i /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/$1.png -o /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/$1_results.txt
# python3 "$posegen" -i "$base_path/$1/photogrammetry/$1.png" -o "$base_path/$1/photogrammetry/$1_results.txt"
python3 "$faceDetect" -- --scan $1 --path "$base_path"

#rig the model
# echo "---------------------"
# echo "---------------------"
# echo "---------------------"
# echo "Rigging the model ..."
# echo "---------------------"
# echo "---------------------"
# echo "---------------------"
# echo /Applications/Blender.app/Contents/MacOS/Blender -b -P /System/Volumes/Data/mnt/scanDrive/software/2.10.22_updates/retarget/AddRig.py -- --scan $1
"$blender" -b -P "$software/AddRig.py" -- --scan $1 --path "$base_path"

#pose test
"$blender" -b -P "$software/poseTest.py" -- "$base_path/$1/photogrammetry/$1-rig.blend"

# run the shots
# echo "-------------------------"
# echo "-------------------------"
# echo "-------------------------"
# echo "Retargeting the model ..."
# echo "-------------------------"
# echo "-------------------------"
# echo "-------------------------"
# echo /System/Volumes/Data/mnt/scanDrive/software/2.10.22_updates/retarget/retargetScan.sh $1
# echo "-------------------------"
# /System/Volumes/Data/mnt/scanDrive/software/2.10.22_updates/retarget/retargetScan.sh $1
# /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/software/5.2.22/sh1100_v56_Retargeting.blend -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/RetargetPlayer.py -- --scan $1 --path /System/Volumes/Data/mnt/scanDrive/takes/
# /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/software/5.2.22/sh1000_EstablishingShot_v020_Retargeting.blend -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/RetargetCharacter_v1.1.py -- --scan $1

# run the shots
# echo "-------------------------"
# echo "-------------------------"
# echo "-------------------------"
# echo "rendering the movie ..."
# echo "-------------------------"
# echo "-------------------------"
# echo "-------------------------"
# echo "-------------------------"
# echo /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/software/5.2.22/movieMaker.blend -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/movieMaker.py -- --scan $1
# /Applications/Blender.app/Contents/MacOS/Blender -b /System/Volumes/Data/mnt/scanDrive/software/5.2.22/movieMaker.SF.blend -P /System/Volumes/Data/mnt/scanDrive/software/5.2.22/movieMaker.py -- --scan $1
