mkdir -p /System/Volumes/Data/mnt/scanDrive/takes/$1/{retarget,render,finalVideo}
mkdir -p /System/Volumes/Data/mnt/scanDrive/takes/$1/render/vfx
/Applications/Blender.app/Contents/MacOS/blender -b /System/Volumes/Data/mnt/scanDrive/software/retargeting/houston/retarget.blend -P /System/Volumes/Data/mnt/scanDrive/software/retargeting/houston/retarget.py -- --scan $1 --path /System/Volumes/Data/mnt/scanDrive/takes
/Applications/Blender.app/Contents/MacOS/blender -b /System/Volumes/Data/mnt/scanDrive/takes/$1/retarget/$1.blend -P /System/Volumes/Data/mnt/scanDrive/software/retargeting/houston/render.py -- --scan $1 --path /System/Volumes/Data/mnt/scanDrive/takes
/Applications/Blender.app/Contents/MacOS/blender -b /System/Volumes/Data/mnt/scanDrive/software/retargeting/houston/moviemaker.blend -P /System/Volumes/Data/mnt/scanDrive/software/retargeting/houston/moviemaker.py -- --scan $1 --path /System/Volumes/Data/mnt/scanDrive/takes
