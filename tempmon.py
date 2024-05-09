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

def FetchEnv(strVarName):
  """
  Function that fetches the specified content of specified environment variable,
  converting nonetype to empty string.
  Parameters:
    strVarName: The name of the environment variable to be fetched
  Returns:
    The content of the environment or empty string
  """

  if os.getenv(strVarName) != "" and os.getenv(strVarName) is not None:
    return os.getenv(strVarName)
  else:
    return ""

def main():

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
  strFilePath = strBaseDir + strScriptName[:iLoc] + ISO + ".CSV"


  print("This is a script to raspberrypi cpu stats. "
          "This is running under Python Version {}".format(strVersion))
  print("Running from: {}".format(strRealPath))
  dtNow = time.strftime("%A %d %B %Y %H:%M:%S %Z")
  print("The time now is {}".format(dtNow))
  print("Output written to {}".format(strFilePath))

  # fetching secrets in environment
  iInt = FetchEnv("MEASUREINT")
  if isInt(iInt):
    print("Interval specification of {} is valid".format(iInt))
    iInt=int(iInt)
  else:
    print("Invalid interval specification:'{}' defaulting to 60".format(iInt))
    iInt = 60

  objFile = open(strFilePath,"a+", encoding="utf8")
  objFile.write("Timestamp,Temperature (°C),Clock Speed (MHz),Throttled\n")
  objvcgm = Vcgencmd()
  while True:
    strCurTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    temp = objvcgm.measure_temp()
    clock = int(objvcgm.measure_clock("arm")/1e6)
    throttled = objvcgm.get_throttled()["breakdown"]["2"]

    string = "{},{},{},{}\n".format(strCurTime,temp,clock,throttled)
    print(string, end="")
    objFile.write(string)
    objFile.flush()
    time.sleep(iInt)

if __name__ == "__main__":
  main()