#!/bin/sh
## Send Video

dirPath="/System/Volumes/Data/mnt/scanDrive/takes/$1"
echo "Received CaptureID: $1"
echo "ProcessID: $2"
videoPath="$dirPath/finalVideo/$1.singleplayer.mp4"
echo $videoPath

curl -X 'POST' \
  "http://backend.scene-machine.com/api/process/finish-singleplayer-video/$2" \
  -H 'accept: */*' \
  -H 'Authorization: Bearer cDOIhwWZhrEzy8RlUC4yRkUFQzZ583XB' \
  -H 'Content-Type: multipart/form-data' \
  -F "video=@$videoPath;type=video/mp4" \
