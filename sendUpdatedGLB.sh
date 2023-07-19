#!/bin/sh
## Send GLBs

dirPath="/System/Volumes/Data/mnt/scanDrive/takes/$1"
echo "Received CaptureID: $1"
echo "ProcessID: $2"
glbPath="$dirPath/glb/$1.glb"
pngPath="$dirPath/glb/$1.png"
echo $glbPath $pngPath

curl -X 'POST' \
  "http://backend.scene-machine.com/api/process/finish-scan/$2" \
  -H 'accept: */*' \
  -H 'Authorization: Bearer cDOIhwWZhrEzy8RlUC4yRkUFQzZ583XB' \
  -H 'Content-Type: multipart/form-data' \
  -F "glb=@$glbPath" \
  -F "imagePreview=@$pngPath;type=image/png"
