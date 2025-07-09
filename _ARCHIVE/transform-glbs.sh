#!/bin/bash

echo "---------- Running GLB transformations ----------"
BASE_PATH=/Volumes/scanDrive/takes/$1/photogrammetry
echo "Using Base Path:" $BASE_PATH

# create the converted directory if it does not exist
mkdir -p /Volumes/scanDrive/takes/$1/photogrammetry/converted

# create an array with all the files/dir
FILES=(/Volumes/scanDrive/takes/$1/photogrammetry/glb/*)

STRING="Frame"

for f in ${!FILES[*]}
do
  	echo "Processing $((f + 1)) of ${#FILES[@]}"
	echo $BASE_PATH
  	echo "$(basename ${FILES[f]} .glb)"
  	# take action on each file. $f store current file name. Make the single frames smaller
	if [[ ${FILES[f] } == *"$STRING"* ]]
	then
		echo "----- PROCESSING FRAME -----"
    	gj-gltf-transform -i $BASE_PATH/glb/$(basename ${FILES[f]}) -o $BASE_PATH/converted/$(basename ${FILES[f]} .glb)_final.glb -s 256
	else
		echo "--------------------------------"
		echo "----- PROCESSING ANIMATION -----"
		echo "--------------------------------"
		gj-gltf-transform -i $BASE_PATH/glb/$(basename ${FILES[f]}) -o $BASE_PATH/converted/$(basename ${FILES[f]} .glb)_final.glb 
  	fi	
done
