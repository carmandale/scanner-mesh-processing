from datetime import datetime
from multiprocessing import Process
from helperFunctions import getProcState, setProcState, setMacState
from scan_db import APP
from config import DATA
import psutil
import requests
import shutil
import time
import traceback

procToKill = [] #["natron.exe", "realitycapture.exe", "ue4editor.exe"]
timeoutSec = 1500

def killProcs(pid):
    pid.terminate()
    pid.join()
    for proc in psutil.process_iter():
        if proc.name().lower() in procToKill:
            proc.kill()

def checkHanging(macName, pid):
    #procInfo = requestDataPost(requestUrl, {'action': 'getProcState', 'macName': macName})
    procInfo = getProcState(macName)
    hanging = False
    if procInfo:
        psStartTime = datetime.strptime(str(procInfo['start_time']), '%Y%m%d%H%M%S')
        currTime = datetime.now()
        elapsedTime = currTime - psStartTime
        elapsedSec = elapsedTime.total_seconds()
        if int(procInfo['wait']) == 0:
            if int(procInfo['wait_intervals']) > 0:
                elapsedSec -= (int(procInfo['wait_intervals']) * 300)
            if elapsedSec > timeoutSec:
                hanging = True
                scanId = procInfo['scan_id']
                killProcs(pid)
                # result = requestDataPost(requestUrl, {'action': 'setFailed', 'macName': macName})
                result = setProcState(macName, "failed")
    return hanging

def startNewScan(macName, procNum):
    scanProc = Process(name="{0}-proc{1}".format(macName, procNum), target=APP)#, args=(DATA))
    # result = requestDataPost(requestUrl, {'action': 'setMacState', 'setState':'ready', 'macName': macName, 'proc':"proc{0}".format(procNum)})
    result = setMacState(macName, 'ready', 'proc{0}'.format(procNum))
    scanProc.start()
    print(scanProc.name)
    return scanProc

if __name__ == '__main__':
    print("Starting Scanner Program")

    while True:
        r = requests.head(DATA["scannerLink"])
        if r.ok:
            break
        print("Unable to connect to the  database. Check Connection. Retrying in 5 secs...")
        time.sleep(5)
    # requestUrl += "/API/actions.php" #API url
    macName = DATA['proc']['macName']

    print("{0} has boot up successfully, and scan processing is being started.".format(macName))
    while True:
        try:
            fh = open(DATA["lookPath"]+"checkMountPoint", "r")
            fh.close()
            print("Mounted scan drive successfully")
            break
        except:
            print("Mounting scan drive failed. Retry in 5 secs...")
            time.sleep(5)

    procNum = 0
    scanProc = startNewScan(macName, procNum)
    while True:
        try:
            print("About to time.sleep for 5 mins")
            time.sleep(300)
            # checkFailed(dbConn)
            if checkHanging(macName, scanProc):
                procNum += 1
                scanProc = startNewScan(macName, procNum)
        except KeyboardInterrupt:
            print("Keyboard Interrupt received for watcher. Exiting process.")
            break
        except:
            print("Got an error processing job.")
            print('-'*60)
            traceback.print_exc()
            print('-'*60)
            break
    # result = requestDataPost(requestUrl, {'action': 'setMacState', 'setState':'stopped', 'macName': macName})
    result = setMacState(macName,'stopped')
    # result = requestDataPost(requestUrl, {'action': 'setFailed', 'macName': macName})
    result = setProcState(macName, 'failed')
    killProcs(scanProc)