import requests
from requests.structures import CaseInsensitiveDict
import os
from time import sleep
from datetime import datetime
from config import DATA

ORI_URL = DATA["scannerLink"]
API_HEADERS = CaseInsensitiveDict()
API_HEADERS["Accept"] = "*/*"
API_HEADERS["Authorization"] = DATA["awsBackend"]["token"]

def requestDataPost(sendUrl, params):
    r = requests.post(url=sendUrl, data=params)
    if r.ok:
        return r.json()
    else:
        return False

def printAndLog(msg, logSeverity=0):
    print(msg)
    # logServer(msg, logSeverity)

def logServer(logMsg, logSeverity):
    # server = "http://192.168.0.132/logger.php"
    server = ORI_URL+"/logger.php"  ## For local network
    currDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    r=requests.post(url=server, data={'message':logMsg, 'date':currDate, 'severity':logSeverity})

def createReqDir(requiredDirs):
    ''' Creates all the required directories under path'''
    for directory in requiredDirs:
        if not os.path.exists(directory):
            os.mkdir(directory)

def isScanStopped(requestUrl, scanId, macName, procState):
    result = requestDataPost(requestUrl, {'action': 'setProcState', 'scanId':scanId, 'procState': procState, 'macName': macName})
    return checkMacReady(requestUrl, macName)

def checkMacReady(requestUrl, macName):
    macStateResult = requestDataPost(requestUrl, {'macName': macName, 'action': 'getMacState'})
    if macStateResult['status'] == "reqPause":
        macStateResult['status'] = "paused"
        result = requestDataPost(requestUrl, {'action': 'setMacState', 'setState': macStateResult['status'], 'macName': macName})
        wait_int = 0
        while macStateResult['status'] == "paused":
            # Sleep for 5 mins, and check again
            sleep(300)
            wait_int += 1
            macStateResult = requestDataPost(requestUrl, {'macName': macName, 'action': 'getMacState'})
        if wait_int:
            result = requestDataPost(requestUrl, {'macName': macName, 'action': 'increaseWaitInt', 'wait_intervals': wait_int})
    if macStateResult['status'] == "reqReady":
        result = requestDataPost(requestUrl, {'action': 'setFailed', 'macName': macName})
        result = requestDataPost(requestUrl, {'action': 'setMacState', 'setState': 'ready', 'macName': macName})
        return True
    elif macStateResult['status'] == "reqProc":
        setState = "processing"
        result = requestDataPost(requestUrl, {'action': 'setMacState', 'setState': setState, 'macName': macName})
    return False

def getProcState(macName):
    url = f'{ORI_URL}/machine/proc/{macName}'
    payload = requests.get(url).json()
    proc = payload['process']
    print(f"{macName}'s current process is {proc}")
    return payload

def setProcState(macName, status):
    if status == "failed":
        url1 = f'{ORI_URL}/failed/{macName}'
    else:
        url1 = f'{ORI_URL}/set_proc/{macName}/{status}'
    requests.put(url1)
    print(f"Process on {macName} has its status set to {status}")
    # url2 = f'{ORI_URL}/machine/proc/{macName}'
    # payload = requests.get(url2).json()
    return True #payload


def setMacState(macName, status, proc=None):
    url1 = f'{ORI_URL}/machine/{macName}/{status}'
    requests.put(url1)
    print(f"{macName}'s status has been set to {status}")
    url2 = f'{ORI_URL}/machine/{macName}'
    payload = requests.get(url2).json()
    return payload


def setScanComplete(captureId):
    url1 = f'{ORI_URL}/scan/completed/{captureId}'
    payload = requests.put(url1).json()
    time_completed = payload['finish_time']
    print(f"Scan {captureId} has been completed at {time_completed}")
    return payload

def getNewScan(macName):
    url = f'{ORI_URL}/get_new_scan/{macName}'
    payload = requests.get(url).json()
    proc = payload['capture_id']
    print(f"{macName}'s current process is {proc}")
    return proc

def getProcLastSuccess(macName):
    url = f'{ORI_URL}/last_success/{macName}'
    payload = requests.get(url).json()
    last_success = payload['last_success']
    print(f"{macName}'s last success was {last_success}")
    return payload

def setProcLastSuccess(macName, last_success):
    url1 = f'{ORI_URL}/last_success/{macName}/{last_success}'
    requests.put(url1)
    print(f"{macName}'s last success has been set to {last_success}")

def getRemoteProcess(macName, processType="scan"):
    processUrl = "{0}/{1}?machineName={2}".format(DATA["awsBackend"]["baseUrl"], DATA["awsBackend"]["getProcessRoute"].format(processType), macName)
    processReq = requests.post(processUrl, headers=API_HEADERS)
    if processReq.status_code == 200:
        processJson = processReq.json()
        if processType == "scan":
            print("Process Received. Type: {0}  --  ID: {1}".format(processJson['type'], processJson['dto']['id']))
        else:
            print("Process Received. Type: {0}  --  GamePlayID: {1}".format(processJson['type'], processJson['dto']['requestedBy']['id']))
        return processJson
    else:
        print("!!! Error: Process not received")
        print(processReq.text)

def finishRemoteProcess(processId, glbPath, imagePreviewPath):
    processUrl = "{0}/{1}/{2}".format(DATA["awsBackend"]["baseUrl"], DATA["awsBackend"]["finishProcessRoute"], processId)
    files = {
        "glb": (f"{processId}.glb", open(glbPath, 'rb')),
        "imagePreview": (f"{processId}.png", open(imagePreviewPath, 'rb'))
    }

    response = requests.post(processUrl, headers=API_HEADERS, files=files, data={})
    if response.status_code == 200:
        print(f"Model and image uploaded successfully! Process {processId} has been marked completed")
    else:
        print("!!! Error: Process not received")
        print(processReq.text)

def resetProcess(processId):
    processUrl = "{0}/{1}/{2}".format(DATA["awsBackend"]["baseUrl"], DATA["awsBackend"]["failProcessRoute"], processId)

    processReq = requests.post(processUrl, headers=API_HEADERS)
    if processReq.status_code == 200:
        print(f"Process {processId} has been marked failed")
    else:
        print("!!! Error: Process not received")
        print(processReq.text)

def sendPlayerVideo(processId, videoPath, player="singleplayer"):
    processUrl = "{0}/{1}/{2}".format(DATA["awsBackend"]["baseUrl"], DATA["awsBackend"]["videoProcessRoute"].format(player), processId)
    files = {
        "video": (f"{processId}.mp4", open(videoPath, 'rb'))
    }

    response = requests.post(processUrl, headers=API_HEADERS, files=files, data={})
    if response.status_code == 200:
        print(f"Player video and image uploaded successfully! Process {processId} has been marked completed")
    else:
        print("!!! Error: Process not received")
        print(processReq.text)
