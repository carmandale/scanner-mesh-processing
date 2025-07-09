# New Code by Ahsan Ali Khoja - ahsan.khoja@gmail.com
# Original Code by Steve Palaia - steve.palaia@gmail.com
# Edited by Daniel Leeper	danieldleeper@gmail.com

import argparse
import glob
import subprocess

USE = "Program for creating and running natron, reality capture, unreal, and ffmpeg commands"
DRY_RUN = False

def argumentHandler():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-d", "--dir", help="Enter the directory path for the images", required=True, dest="images_dir")
    parser.add_argument("--photogrammetry_path", help="Enter the path for photogrammetry program", dest="photogrammetry_program_path")
    parser.add_argument("--photogrammetry_detail", help="Enter the detail for photogrammetry program", dest="photogrammetry_program_detail")
    parser.add_argument("--rignet_path", help="Enter the path for the rignet program", dest="rignet_program_path")
    parser.add_argument("--blender_path", help="Enter the path for the blender python script", dest="blender_python_scr_path")
    parser.add_argument("--dry_run", help="Using this flag prints the output/commands rather than running it", dest="dry_run", default=False, action="store_true")

    return parser.parse_args()

def photogrammetryCommand(photogrammetryPath, imagesDir, outputPath, detail="medium"):
    """
        Function that creates the photogrammetry command.
    """
    #return "{0} {1} {2} --detail={3} -o sequential".format(photogrammetryPath, imagesDir, outputPath, detail)
    return "{0} {1} {2} --detail={3}".format(photogrammetryPath, imagesDir, outputPath, detail)

def cleanUpUSDCCommand(blenderPath, blendPyPath, captureId, facing=0.5):
    """
        Function that creates the python blender script command.
    """
    cleanUpCmd = "{0} -b -P {1} -- --scan {2} --facing {3}".format(blenderPath, blendPyPath, captureId, facing)
    return cleanUpCmd

def mlPoseCommand(pyScriptPath, inputFile, outputFile):
    """
        Function that creates the mlRig command.
    """
    return "python {0} -i {1} -o {2}".format(pyScriptPath, inputFile, outputFile)

def rigifyCommand(blenderPath, blendPyPath, captureId):
    """
        Function that creates the rigNet command.
    """
    return "{0} -b -P {1} -- --scan {2}".format(blenderPath, blendPyPath, captureId)

# def retargetCommand(retargetScriptPath, captureId):
#     """
#         Function that creates the retarget command.
#     """
#     return "{0} {1}".format(retargetScriptPath, captureId)

def retargetCommand(blenderPath, blendFilePath, blendPyPath, captureId, scanPath):
    """
        Function that creates the retarget command.
    """
    return "{0} -b {1} -P {2} -- --scan {3} --path {4}/".format(blenderPath, blendFilePath, blendPyPath, captureId, scanPath)

def transformCommand(transformScriptPath, captureId):
    """
        Function that creates the transform command.
    """
    return "{0} {1}".format(transformScriptPath, captureId)

def shotCommand(blenderPath, blendFilePath, blendPyPath, captureId, shot):
    blendFilePath = blendFilePath.format(shot)
    return "{0} -b {1} -P {2} -- --scan {3} --shot {4}".format(blenderPath, blendFilePath, blendPyPath, captureId, shot)

def movieMakerCommand(blenderPath, blendFilePath, blendPyPath, captureId):
    return "{0} -b {1} -P {2} -- --scan {3}".format(blenderPath, blendFilePath, blendPyPath, captureId)

def rigNetCommand(rigNetPath, inputFile, outputPath):
    """
        Function that creates the rigNet command.
    """
    return "{0} {1} {2}".format(rigNetPath, inputFile, outputPath)

def blenderCommand(blenderPath, inputFile, outputPath):
    """
        Function that creates the rigNet command.
    """
    return "{0} {1} {2}".format(blenderPath, inputFile, outputPath)

def defaultBlenderCommand(blenderPath, blendFilePath, blendPyPath, captureId, scanPath="/System/Volumes/Data/mnt/scanDrive2/takes/"):
    """
        Function that generates a generic commandLine blender command command.
    """
    return f"{blenderPath} -b {blendFilePath} -P {blendPyPath} -- --scan {captureId} --path {scanPath}"

if __name__ == "__main__":
    args = vars(argumentHandler())
    #print(args)
    DRY_RUN = args["dry_run"]

    imagesDir = args["images_dir"]
    photogrammetryOut = "{0}/processed/final.usdz".format(imagesDir)
    rigNetOut = "{0}/processed/final.blend".format(imagesDir)
    blenderOut = "{0}/processed/final.mp4".format(imagesDir)
    print(photogrammetryCommand(args["photogrammetry_program_path"], imagesDir, photogrammetryOut, args["photogrammetry_program_detail"]))
    print(rigNetCommand(args["rignet_program_path"], photogrammetryOut, rigNetOut))
    print(blenderCommand(args["blender_python_scr_path"], rigNetOut, blenderOut))

## Folders to be created in the bash file -- connecting script
#/Users/groovejones/Library/Developer/Xcode/DerivedData/HelloPhotogrammetry-avkvbrbokvbhhmewlhejkyzbgjdl/Build/Products/Debug/HelloPhotogrammetry <input-folder> <output-filename> [--detail <detail>]
