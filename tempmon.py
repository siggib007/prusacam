'''
Script that capture CPU stats
for a RaspberryPI and write to a CSV

Author Siggi Bjarnason 08 may 2024
Copyright 2024 Siggi Bjarnason

Following packages need to be installed
pip install vcgencmd

'''
# Import libraries
import sys
import os
import time
from vcgencmd import Vcgencmd
import argparse
import inputimeout

def timed_input(prompt, timeout):
    try:
        return inputimeout.inputimeout(prompt=prompt, timeout=timeout)
    except inputimeout.TimeoutOccurred:
        return None

def isInt(CheckValue):
    """
    function to safely check if a value can be interpreded as an int
    Parameter:
      Value: A object to be evaluated
    Returns:
      Boolean indicating if the object is an integer or not.
    """
    if isinstance(CheckValue, (float, int, str)):
        try:
            fTemp = int(CheckValue)
        except ValueError:
            fTemp = "NULL"
    else:
        fTemp = "NULL"
    return fTemp != "NULL"

def main():

  objParser = argparse.ArgumentParser(description="Raspberry Pi Monitor")
  objParser.add_argument("--silent", dest="silent",
                      action="store_true", help="only output to file, not to screen")
  objParser.add_argument("--sleep", dest="sleep_time", type=int,
                      help="Number of seconds to sleep inbetween checks, default is 60")
  objParser.add_argument("--filename", dest="file_name", type=str, help="Output file name, "
                         "defaults to {scriptname}-iso-date.csv in the script directory")

  objArgs = objParser.parse_args()
  if objArgs.sleep_time is not None:
    iSleepSec = objArgs.sleep_time
  else:
     iSleepSec = 60

  ISO = time.strftime("-%Y-%m-%d-%H-%M-%S")
  strVersion = "{0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
  strRealPath = os.path.realpath(sys.argv[0])
  strBaseDir = os.path.dirname(sys.argv[0])
  if strBaseDir == "":
    iLoc = strRealPath.rfind("/")
    strBaseDir = strRealPath[:iLoc]
  if strBaseDir[-1:] != "/":
    strBaseDir += "/"
  strScriptName = os.path.basename(sys.argv[0])
  iLoc = strScriptName.rfind(".")
  strFilePath = strBaseDir + strScriptName[:iLoc] + ISO + ".csv"
  if objArgs.file_name is not None:
     strFilePath=objArgs.file_name

  if not objArgs.silent:
    print("This is a script to raspberrypi cpu stats. "
            "This is running under Python Version {}".format(strVersion))
    print("Running from: {}".format(strRealPath))
    dtNow = time.strftime("%A %d %B %Y %H:%M:%S %Z")
    print("The time now is {}".format(dtNow))
    print("Output written to {}".format(strFilePath))

  objFile = open(strFilePath,"a+", encoding="utf8")
  objFile.write("Timestamp,Temperature (°C),Clock Speed (MHz),Throttled\n")
  objvcgm = Vcgencmd()
  bContinue = True
  while bContinue:
    strCurTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    fTempiture = objvcgm.measure_temp()
    iClockSpeed = int(objvcgm.measure_clock("arm")/1e6)
    bThrottled = objvcgm.get_throttled()["breakdown"]["2"]

    strOut = "{},{},{},{}\n".format(strCurTime,fTempiture,iClockSpeed,bThrottled)
    if not objArgs.silent:
      print(strOut, end="")
    objFile.write(strOut)
    objFile.flush()
    if objArgs.silent:
      time.sleep(iSleepSec)
    else:
      strResp = timed_input("Sleeping for {} seconds, enter q to exit ...".format(iSleepSec),iSleepSec)
      if isinstance(strResp,str):
        if len(strResp) > 0:
            if strResp.lower()[0] == "q":
              bContinue = False

if __name__ == "__main__":
  main()