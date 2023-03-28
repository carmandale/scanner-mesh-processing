#!/bin/sh
## Send GLBs

dirPath="/Volumes/scanDrive2/takes/$1"
echo "Received CaptureID: $1"
commandFile="$dirPath/commands.sh"
echo "ReadFile: $commandFile"
read -r firstLine<$commandFile
processId=$(echo $firstLine | cut -d ' ' -f 3)
#firstLine=$(head -n 1 $commadFile)
#echo $firstLine
echo "ProcessID: $processId"
glbPath="$dirPath/glb/$1.glb"
pngPath="$dirPath/glb/$1.png"
echo $glbPath $pngPath

curl -X 'POST' \
  "http://backend.scene-machine.com/api/process/finish-scan/$processId" \
  -H 'accept: */*' \
  -H 'Authorization: Bearer cDOIhwWZhrEzy8RlUC4yRkUFQzZ583XB' \
  -H 'Content-Type: multipart/form-data' \
  -F "glb=@$glbPath" \
  -F "imagePreview=@$pngPath;type=image/png"
