#!/bin/sh
## Send GLBs

dirPath="/Users/administrator/groove-test/takes/$1"
echo "Received CaptureID: $1"
blendPath="$dirPath/photogrammetry/$1-rig.blend"
poseImgPath="$dirPath/photogrammetry/pose-test.png"
echo $blendPath $poseImgPath
echo $1 $2

curl -X 'POST' \
  "http://backend.lgmaxout.com/api/process/finish-scan/$2" \
  -H 'accept: */*' \
  -H 'Authorization: Bearer cDOIhwWZhrEzy8RlUC4yRkUFQzZ583XB' \
  -H 'Content-Type: multipart/form-data' \
  -F "blendFile=@$blendPath" \
  -F "imagePreview=@$poseImgPath;type=image/png"
