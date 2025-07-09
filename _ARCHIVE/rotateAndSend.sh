python /Users/administrator/groove-test/software/scannermeshprocessing-2023/pose_gen_package/face_detector.py -- --scan $1 --path /Users/administrator/groove-test/takes
/Applications/Blender.app/Contents/MacOS/Blender -b -P /Users/administrator/groove-test/software/scannermeshprocessing-2023/AddRig.py -- --scan $1
/Applications/Blender.app/Contents/MacOS/Blender -b -P /Users/administrator/groove-test/software/scannermeshprocessing-2023/poseTest.py -- /Users/administrator/groove-test/takes/$1/photogrammetry/$1-rig.blend
sh /Users/administrator/groove-test/software/03.01.23/sendUpdatedBlend.sh $1 
