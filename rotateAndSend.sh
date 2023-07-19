python /System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/pose_gen_package/face_detector.py -- --scan $1 --path /System/Volumes/Data/mnt/scanDrive/takes
/Applications/Blender.app/Contents/MacOS/Blender -b -P /System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/AddRig.py -- --scan $1
/Applications/Blender.app/Contents/MacOS/Blender -b -P /System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/poseTest.py -- /System/Volumes/Data/mnt/scanDrive/takes/$1/photogrammetry/$1-rig.blend
sh /System/Volumes/Data/mnt/scanDrive/software/03.01.23/sendUpdatedBlend.sh $1 
