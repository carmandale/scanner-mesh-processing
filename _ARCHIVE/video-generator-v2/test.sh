#mkdir /Users/groovejones/scene_machine/sequence/takes/20220106170311/render
#mkdir /Users/groovejones/scene_machine/sequence/takes/20220106170311/finalVideo
#/Users/groovejones/scene_machine/sequence/utility/groove-mesher2022-01-06-12-33-17/groove-mesher /Users/groovejones/scene_machine/sequence/takes/20220106170311/source /Users/groovejones/scene_machine/sequence/takes/20220106170311/photogrammetry/ --detail=medium
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/utility/cleanup_script/cleanup_v11.blend -P /Users/groovejones/scene_machine/sequence/utility/cleanup_script/stripper_v11.py -- --scan 20220106170311
python /Users/groovejones/Software/pose_gen_package/pose_generator.py -i /Users/groovejones/scene_machine/sequence/takes/20220106170311/photogrammetry/20220106170311.png -o /Users/groovejones/scene_machine/sequence/takes/20220106170311/photogrammetry/20220106170311_results.txt
/Applications/Blender.app/Contents/MacOS/Blender -b -P /Users/groovejones/scene_machine/sequence/utility/rig_script/AddRig.py -- --scan 20220106170311
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/sh1450/sh1450.blend -P /Users/groovejones/scene_machine/sequence/runShots.py -- --scan 20220106170311 --shot sh1450
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/sh1300/sh1300.blend -P /Users/groovejones/scene_machine/sequence/runShots.py -- --scan 20220106170311 --shot sh1300
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/sh1600/sh1600.blend -P /Users/groovejones/scene_machine/sequence/runShots.py -- --scan 20220106170311 --shot sh1600
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/sh1800/sh1800.blend -P /Users/groovejones/scene_machine/sequence/runShots.py -- --scan 20220106170311 --shot sh1800
/Applications/Blender.app/Contents/MacOS/Blender -b /Users/groovejones/scene_machine/sequence/movieMaker.blend -P /Users/groovejones/scene_machine/sequence/movieMaker.py -- --scan 20220106170311

