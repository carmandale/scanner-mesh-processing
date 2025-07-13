from ProcessRawScannerImages import defaultBlenderCommand, movieMakerCommandMP
from helperFunctions import *
import importlib
import config
from config import DATA
from subprocess import run as subprocessRun
import time
import traceback
import argparse
import os
from random import random

takesDir = "{0}{1}".format(DATA['mountPath'], DATA['lookPath'])
softwareDir = "{0}{1}".format(DATA['mountPath'], DATA['softwareDir'])
USE = "Program for running the MultiPlayer Video jobs"
TOTAL_RENDER_COUNT = 982

def argumentHandler():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-p0", "--p0CaptureId", help="Enter the p0CaptureId", dest="p0CaptureId")
    parser.add_argument("-p1", "--p1CaptureId", help="Enter the p1CaptureId", dest="p1CaptureId")
    parser.add_argument("-j", "--jump", help="Enter the jump boolean", dest="jump")
    parser.add_argument("-w", "--winner", help="Enter the winner index", dest="winner")
    parser.add_argument("-o", "--videoName", help="Enter the ", dest="videoName")
    parser.add_argument("--dry_run", help="Using this flag prints the output/commands rather than running it", dest="dry_run", default=False, action="store_true")

    return parser.parse_args()

def videoExist(p0VideoPath, p1VideoPath):
    # Check if video exists and return True of False
    status = False
    if os.path.exists(p0VideoPath) and not os.path.exists(p1VideoPath):
        subprocessRun(f"/bin/cp {p0VideoPath} {p1VideoPath}".split())
        status = True
    elif os.path.exists(p1VideoPath) and not os.path.exists(p0VideoPath):
        subprocessRun(f"/bin/cp {p1VideoPath} {p0VideoPath}".split())
        status = True
    return status

def multiPlayerVideoGen(p0CaptureId, p1CaptureId, jump, winner, videoName, gamePlayId="testing", dry_run=False):
    importlib.reload(config)
    from config import DATA
    blenderPath = DATA["blender"]["exePath"]

    p0ScanPath = "{0}/{1}".format(takesDir, p0CaptureId)
    p1ScanPath = "{0}/{1}".format(takesDir, p1CaptureId)
    videoPath = f"{p0ScanPath}/finalVideo/{p0CaptureId}.multiplayer.mp4"
    renameVideoPath = f"{p0ScanPath}/finalVideo/{videoName}.multiplayer.mp4"
    p1VideoPath = f"{p1ScanPath}/finalVideo/{videoName}.multiplayer.mp4"

    if videoExist(renameVideoPath, p1VideoPath):
        return

    allCommands = list()
    p0RenderPath = f"{p0ScanPath}/render/multiplayer/player0/"
    p1RenderPath = f"{p1ScanPath}/render/multiplayer/player0/"

    p0Count = 0
    if os.path.exists(p0RenderPath):
        for root_dir, cur_dir, files in os.walk(p0RenderPath):
            p0Count += len(files)
    print('Render File count:', p0Count)

    if p0Count == TOTAL_RENDER_COUNT:
        p0BlendRenderIn_0 = "{0}/{1}".format(p0ScanPath, DATA["render"]["blendFileMP"].format(p0CaptureId, 0))
        p0BlendRenderIn_1 = "{0}/{1}".format(p0ScanPath, DATA["render"]["blendFileMP"].format(p0CaptureId, 1))
        p0RetargetCmd = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["retarget"]["blendFileMP"]), "{0}{1}".format(softwareDir, DATA["retarget"]["blenderScriptMP"]), p0CaptureId, takesDir)
        p0RenderCmd_0 = defaultBlenderCommand(blenderPath, p0BlendRenderIn_0, "{0}{1}".format(softwareDir, DATA["render"]["blenderScriptMP"]), p0CaptureId, takesDir)
        p0RenderCmd_1 = defaultBlenderCommand(blenderPath, p0BlendRenderIn_1, "{0}{1}".format(softwareDir, DATA["render"]["blenderScriptMP"]), p0CaptureId, takesDir)
        allCommands += [p0RetargetCmd, p0RenderCmd_0, p0RenderCmd_1]

    p1Count = 0
    if os.path.exists(p1RenderPath):
        for root_dir, cur_dir, files in os.walk(p1RenderPath):
            p1Count += len(files)
    print('Render File count:', p1Count)

    if p0Count == TOTAL_RENDER_COUNT:
        p1BlendRenderIn_0 = "{0}/{1}".format(p1ScanPath, DATA["render"]["blendFileMP"].format(p1CaptureId, 0))
        p1BlendRenderIn_1 = "{0}/{1}".format(p1ScanPath, DATA["render"]["blendFileMP"].format(p1CaptureId, 1))
        p1RetargetCmd = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["retarget"]["blendFileMP"]), "{0}{1}".format(softwareDir, DATA["retarget"]["blenderScriptMP"]), p1CaptureId, takesDir)
        p1RenderCmd_0 = defaultBlenderCommand(blenderPath, p1BlendRenderIn_0, "{0}{1}".format(softwareDir, DATA["render"]["blenderScriptMP"]), p1CaptureId, takesDir)
        p1RenderCmd_1 = defaultBlenderCommand(blenderPath, p1BlendRenderIn_1, "{0}{1}".format(softwareDir, DATA["render"]["blenderScriptMP"]), p1CaptureId, takesDir)
        allCommands += [p1RetargetCmd, p1RenderCmd_0, p1RenderCmd_1]

    # movieMakerCmd = defaultBlenderCommand(blenderPath, "{0}{1}".format(softwareDir, DATA["movieMaker"]["blendFileMP"]), "{0}{1}".format(softwareDir, DATA["movieMaker"]["blenderScriptMP"]), captureId, takesDir)
    movieMakerCmdMP = movieMakerCommandMP(blenderPath, "{0}{1}".format(softwareDir, DATA["movieMaker"]["blendFileMP"]), "{0}{1}".format(softwareDir, DATA["movieMaker"]["blenderScriptMP"]), p0CaptureId, p1CaptureId, jump, winner)

    renameVideoCmd = f"/bin/mv {videoPath} {renameVideoPath}"
    copyToP1Cmd = f"/bin/cp {renameVideoPath} {p1VideoPath}"

    allCommands += [movieMakerCmdMP, renameVideoCmd, copyToP1Cmd]
    allCommandsStr = '\n'.join(allCommands)

    commandFile = "{0}/mpVideos/{1}.commands.multiplayer.sh".format(takesDir, videoName)
    print("Creating Commands Files at: ", commandFile)
    writer = open(commandFile, "w")
    print(f"### GamePlayID: {gamePlayId}", file=writer)
    print(allCommandsStr, file=writer)
    writer.close()
    print("Commands written to files: ", commandFile)

    if dry_run:
        print(allCommandsStr)
    else:
        t1 = time.time()

        for command in allCommands:
            subprocessRun(command.split())

        t1 = time.time() - t1

        timeMsg = "Time took to finish scan {0}: {1}".format(videoName, t1)

        printAndLog(timeMsg, 0)
    sendPlayerVideo(gamePlayId, renameVideoPath, "multiplayer")

def APP(dry_run=False):
    macName = DATA['proc']['macName']
    processingState = False
    gamePlayId = None

    while True:
        try:
            # import json
            # currProcess = json.load(open("testVideo.json"))
            currProcess = getRemoteProcess(macName, processType="video")
            print(currProcess)

            # captureId = getNewScan(macName)
            # if captureId:

            if currProcess:
                if currProcess['type'] == 'Video':
                    videoName = currProcess['dto']['requestedBy']['lobbyId']

                    requestor = currProcess['dto']['requestedBy']
                    otherPlayer = currProcess['dto']['other']
                    gamePlayId =  requestor["id"]

                    if requestor["isHost"]:
                        p0Obj = requestor
                        p1Obj = otherPlayer
                    else:
                        p0Obj = otherPlayer
                        p1Obj = requestor

                    p0CaptureId = "superFan" if p0Obj["defaultAvatar"] else p0Obj["captureId"]
                    p1CaptureId = "superFan" if p1Obj["defaultAvatar"] else p1Obj["captureId"]

                    jump = 1 if random() <= 0.9 else 0

                    winner = 0 if p0Obj["playerTime"] < p1Obj["playerTime"] else 1

                    multiPlayerVideoGen(p0CaptureId, p1CaptureId, jump, winner, videoName, gamePlayId, dry_run)
            else:
                time.sleep(60)
                #macReady = checkMacReady()
        except KeyboardInterrupt:
            # if processingState:
            #     resetProcess(processId)
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

            continue

if __name__ == '__main__':
    from config import DATA

    print("{0} has boot up successfully, and scan processing is being started.".format(DATA['proc']['macName']))

    args = vars(argumentHandler())
    dry_run = args["dry_run"]
    p0CaptureId = args["p0CaptureId"]
    p1CaptureId = args["p1CaptureId"]
    jump = args["jump"]
    winner = args["winner"]
    videoName = args["videoName"]

    print(args)


    if p0CaptureId:
        print(captureId, dry_run)
        videoPath = multiPlayerVideoGen(p0CaptureId, p1CaptureId, jump, winner, videoName, "testing", dry_run)
    else:
        print("No Capture ID. Will start APP")
        APP(dry_run)
    # main()