from ProcessRawScannerImages import photogrammetryCommand, cleanUpUSDCCommand, mlPoseCommand, rigifyCommand, retargetCommand, movieMakerCommand, defaultBlenderCommand
from helperFunctions import *
import importlib
import config
from config import DATA
from subprocess import run as subprocessRun
import time
import traceback
import argparse

takesDir = "{0}{1}".format(DATA['mountPath'], DATA['lookPath'])
softwareDir = "{0}{1}".format(DATA['mountPath'], DATA['softwareDir'])
USE = "Program for running the scan process jobs"

def argumentHandler():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-c", "--capture_id", help="Enter the captureId", dest="capture_id")
    parser.add_argument("--dry_run", help="Using this flag prints the output/commands rather than running it", dest="dry_run", default=False, action="store_true")

    return parser.parse_args()

def processScan(processId, captureId, dry_run=False):
    importlib.reload(config)
    from config import DATA

    scanPath = "{0}/{1}".format(takesDir, captureId)
    imagePath = "{0}/{1}".format(scanPath, DATA["scan"]["inDir"])
    macName = DATA['proc']['macName']
    blenderPath = DATA["blender"]["exePath"]
    commandFile = "{0}/commands.sh".format(scanPath)
    tarPath = "{0}{1}/{2}.tar.gz".format(DATA['mountPath'], DATA['tarPath'], captureId)

    glbPath = f"{scanPath}/glb/{captureId}.glb"
    imagePreviewPath = f"{scanPath}/glb/{captureId}.png"
    spVideoPath = f"{scanPath}/finalVideo/{captureId}.singleplayer.mp4"

    requiredDirs = [
        DATA["groove-mesher"]["outDir"],
        DATA["blender"]["renderDir"],
        DATA["blender"]["outDir"]
    ]
    requiredDirs = ["{0}/{1}".format(scanPath, val) for val in requiredDirs]
    usdzOut = requiredDirs[0]+"/"
    mlPoseIn = "{0}/{1}{2}".format(requiredDirs[0], captureId, DATA["mlPose"]["input_suffix"])
    mlPoseOut = "{0}/{1}{2}".format(requiredDirs[0], captureId, DATA["mlPose"]["output_suffix"])

    spBlendRenderIn = "{0}/{1}".format(scanPath, DATA["render"]["blendFileSP"].format(captureId))

    photogrammetryCmd = photogrammetryCommand(DATA["groove-mesher"]["exePath"], imagePath, usdzOut, DATA["groove-mesher"]["detail"])
    cleanUpCmd = cleanUpUSDCCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["blenderCleanup"]["blenderScript"]), captureId, DATA["blenderCleanup"]["facing"])
    mlPoseCmd = mlPoseCommand(DATA["mlPose"]["poseScript"], mlPoseIn, mlPoseOut)
    rigifyCmd = rigifyCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["rigify"]["rigScript"]), captureId)

    retargetGameCmd = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["retarget"]["blendFileGame"]), "{0}{1}".format(softwareDir, DATA["retarget"]["blenderScriptGame"]), captureId, takesDir)
    retargetSPCmd = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["retarget"]["blendFileSP"]), "{0}{1}".format(softwareDir, DATA["retarget"]["blenderScriptSP"]), captureId, takesDir)
    renderSPCmd = defaultBlenderCommand(blenderPath, spBlendRenderIn, "{0}{1}".format(softwareDir, DATA["render"]["blenderScriptSP"]), captureId, takesDir)
    movieMakerCmdSP = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["movieMaker"]["blendFileSP"]), "{0}{1}".format(softwareDir, DATA["movieMaker"]["blenderScriptSP"]), captureId, takesDir)

    # retargetCmd = retargetCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["retarget"]["blendFile"]), "{0}{1}".format(softwareDir, DATA["retarget"]["blenderScript"]), captureId, takesDir)
    # movieMakerCmd = movieMakerCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["movieMaker"]["blendFile"]), "{0}{1}".format(softwareDir, DATA["movieMaker"]["blenderScript"]), captureId)

    printAndLog(scanPath, 0)
    allCommands = '\n'.join([photogrammetryCmd, cleanUpCmd, mlPoseCmd, rigifyCmd, retargetGameCmd, retargetSPCmd, renderSPCmd, movieMakerCmdSP])

    # subprocessRun(f"/usr/bin/tar -xzf {tarPath} -C {takesDir}".split())

    print("Creating Commands File at: ", commandFile)
    writer = open(commandFile, "w")
    print(f"### ProcessId: {processId}", file=writer)
    print(allCommands, file=writer)
    writer.close()
    print("Commands written to file: ", commandFile)

    if dry_run:
        print(allCommands)
    else:

        t1 = time.time()

        createReqDir(requiredDirs)

        subprocessRun(photogrammetryCmd.split())
        # setProcLastSuccess(macName, "usdz")

        subprocessRun(cleanUpCmd.split())
        # setProcLastSuccess(macName, "cleanObj")

        subprocessRun(mlPoseCmd.split())
        # setProcLastSuccess(macName, "mlPose")

        subprocessRun(rigifyCmd.split())
        # setProcLastSuccess(macName, "rigify")

        subprocessRun(retargetGameCmd.split())

        if processId:
            finishRemoteProcess(processId, glbPath, imagePreviewPath)

        subprocessRun(retargetSPCmd.split())

        subprocessRun(renderSPCmd.split())

        subprocessRun(movieMakerCmdSP.split())

        if processId:
            sendPlayerVideo(processId, spVideoPath, "singleplayer")

        # subprocessRun(retargetCmd.split())
        # setProcLastSuccess(macName, "createGlb")

        # subprocessRun(movieMakerCmd.split())
        # setProcLastSuccess(macName, "compressGlb")

        # subprocessRun()

        t1 = time.time() - t1
        timeMsg = "Time took to finish scan {0}: {1}".format(captureId, t1)
        printAndLog(timeMsg, 0)

    return True, glbPath, imagePreviewPath, spVideoPath

def APP(dry_run=False):
    macName = DATA['proc']['macName']
    processingState = False
    processId = None

    while True:
        try:
            currProcess = getRemoteProcess(macName)
            print(currProcess)

            # captureId = getNewScan(macName)
            # if captureId:

            if currProcess:
                if currProcess['type'] == 'Scan':
                    captureId = currProcess['dto']['scan']['captureId']
                    glbPath = f"{takesDir}/{captureId}/glb/{captureId}.glb"
                    imagePreviewPath = f"{takesDir}/{captureId}/glb/{captureId}.png"
                    spVideoPath = f"{takesDir}/{captureId}/finalVideo/{captureId}.singleplayer.mp4"
                    processId = currProcess['dto']['id']
                    printAndLog("Scan {0} Detected - Starting process in 10 secs".format(captureId), 0)
                    # result = setMacState(macName, 'processing')
                    time.sleep(9)

                    processingState = True
                    moveNext, glbPath, imagePreviewPath, spVideoPath = processScan(processId, captureId, dry_run)
                    if moveNext:
                        print("Processing complete!")
                        print(f"  - GLB Path: {glbPath}\n  - Image Preview Path: {imagePreviewPath}\n  - Single Player Video: {spVideoPath}")
                        # result = setScanComplete(captureId)
                        processingState = False
                elif currProcess['type'] == 'Video':
                    videoName = currProcess['dto']['host']['lobbyId']

                    p1CaptureId = currProcess['dto']['host']['captureId']
                    p2CaptureId = currProcess['dto']['client']['captureId']
                    pass 
            else:
                time.sleep(60)
                #macReady = checkMacReady()
        except KeyboardInterrupt:
            if processId and processingState:
                resetProcess(processId)
            printAndLog("Keyboard Interrupt received. Exiting process.", 0)
            break
        except:
            # scanPath = "{0}/{1}".format(takesDir, captureId)
            errorFile = "{0}/errors.txt".format(takesDir)
            writer = open(errorFile, "w+")

            print("Got an error processing job.", file=writer)
            printAndLog("Got an error processing job.", 1)
            print('-'*60)
            errTrace = traceback.format_exc()
            print(errTrace, file=writer)
            printAndLog(errTrace, 2)
            print('-'*60)
            print("Moving to next available job.", file=writer)
            printAndLog("Moving to next available job.", 0)
            writer.close()

            # result = setProcState(macName, 'failed')
            # result = setMacState(macName, 'ready')
            continue

if __name__ == '__main__':
    print("{0} has boot up successfully, and scan processing is being started.".format(DATA['proc']['macName']))

    args = vars(argumentHandler())
    dry_run = args["dry_run"]
    captureId = args["capture_id"]

    if captureId:
        print(captureId, dry_run)
        moveNext = processScan(None, captureId, dry_run)
    else:
        print("No Capture ID. Will start APP")
        APP(dry_run)