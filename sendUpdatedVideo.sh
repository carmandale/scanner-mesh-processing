#!/bin/sh
## Send Video

dirPath="/Volumes/scanDrive2/takes/$1"
echo "Received CaptureID: $1"
commandFile="$dirPath/commands.sh"
echo "ReadFile: $commandFile"
read -r firstLine<$commandFile
processId=$(echo $firstLine | cut -d ' ' -f 3)
#firstLine=$(head -n 1 $commadFile)
#echo $firstLine
echo "ProcessID: $processId"
videoPath="$dirPath/finalVideo/$1.singleplayer.mp4"
echo $videoPath

curl -X 'POST' \
  "http://backend.scene-machine.com/api/process/finish-singleplayer-video/$processId" \
  -H 'accept: */*' \
  -H 'Authorization: Bearer cDOIhwWZhrEzy8RlUC4yRkUFQzZ583XB' \
  -H 'Content-Type: multipart/form-data' \
  -F "video=@$videoPath;type=video/mp4" \
