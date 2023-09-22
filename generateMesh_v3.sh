#!/bin/sh

# Assign the first command line argument to the scan_id variable
scan_id="$1"

# Check if the second command line argument is provided
if [ -z "$2" ]; then
  # If the second argument is not provided, use a predefined default path
  base_path="/Users/administrator/groove-test/takes"
else
  # If the second argument is provided, use it as the base path
  base_path="$2"
fi

if [ -z "$3" ]; then
  # If the third argument is not provided, use normal
  feature_sensitivity="normal"
else
  # If the third argument is provided, use it as feature sensitivity
  feature_sensitivity="$3"
fi


input_folder="$base_path/$1/source/"
output_folder="$base_path/$1/photogrammetry/"

# Print the values of the scan_id and base_path variables
echo "Scan ID: $scan_id"
echo "Base path: $base_path"
echo "Source folder: $input_folder"
echo "Output folder: $output_folder"

# generate the mesh
blender="/Applications/Blender.app/Contents/MacOS/Blender"
# grooveMesher="/Users/administrator/groove-test/software/scannermeshprocessing-2023/groove-mesher-BBox-5/groove-mesher"
grooveMesher="/Users/groovejones/Software/builds/groove-mesher"
grooveMeshCheck="/Users/administrator/groove-test/software/scannermeshprocessing-2023/grooveMeshCheck_v3.py"
prepUSDZ="/Users/administrator/groove-test/software/scannermeshprocessing-2023/prepUSDZ_v3.py"
# generate the preview.usdz file
"$grooveMesher" "$input_folder" "$output_folder" --create-preview # --create-final-model --no-bounds -d medium
# find the bounding box of the mesh
"$blender" -b -P "$grooveMeshCheck" -- "$scan_id" "$base_path/$scan_id/photogrammetry/preview.usdz" "$prepUSDZ" "$grooveMesher" "$input_folder" "$output_folder" "$feature_sensitivity"

