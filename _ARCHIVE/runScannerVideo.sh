mkdir -p /Users/administrator/groove-test/takes/$1/{retarget,render,finalVideo}
mkdir -p /Users/administrator/groove-test/takes/$1/render/vfx
/Applications/Blender.app/Contents/MacOS/blender -b /Users/administrator/groove-test/software/retargeting/houston/retarget.blend -P /Users/administrator/groove-test/software/retargeting/houston/retarget.py -- --scan $1 --path /Users/administrator/groove-test/takes
/Applications/Blender.app/Contents/MacOS/blender -b /Users/administrator/groove-test/takes/$1/retarget/$1.blend -P /Users/administrator/groove-test/software/retargeting/houston/render.py -- --scan $1 --path /Users/administrator/groove-test/takes
/Applications/Blender.app/Contents/MacOS/blender -b /Users/administrator/groove-test/software/retargeting/houston/moviemaker.blend -P /Users/administrator/groove-test/software/retargeting/houston/moviemaker.py -- --scan $1 --path /Users/administrator/groove-test/takes
