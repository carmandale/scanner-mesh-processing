#!/bin/bash

# copy the list of directories above to a certain path

source_path="/Volumes/gjc/productions/Wasserman_CFP2210/rawFootage/backup/takes"

destination="/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/CFP_backwards"

# loop through the list of directories and copy them to the destination
for dir in $(cat backwards.txt); do
    cp -R "$source_path/$dir" "$destination"
done


echo "The directories have been copied to $destination."