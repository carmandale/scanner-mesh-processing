import json

dataFile = open("config.json", "r")
DATA = json.load(dataFile)
dataFile.close()

machineDataFile = open("mac-config.json", "r")
machineData = json.load(machineDataFile)
machineDataFile.close()
DATA = {**DATA, **machineData}