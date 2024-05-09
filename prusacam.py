'''
Script that takes pictures using picamera2
then posts them to Prusa connect

Author Siggi Bjarnason 07 may 2024
Copyright 2024 Siggi Bjarnason

Following packages need to be installed
pip install requests

'''
# Import libraries
import os
import time
import platform
import sys
import requests
from picamera2 import Picamera2

if sys.version_info[0] > 2:
    import urllib.parse as urlparse
    # The following line surpresses a warning that we aren't validating the HTTPS certificate
    requests.urllib3.disable_warnings()
else:
   print("This script is only supported on python 3")
   sys.exit(9)

# End imports

# Few globals
tLastCall = 0
iTotalSleep = 0

# Define few Defaults
iLogLevel = 4  # How much logging should be done. Level 10 is debug level, 0 is none
iTimeOut = 180  # Max time in seconds to wait for network response
iMinQuiet = 2  # Minimum time in seconds between API calls

# sub defs
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

def takePic(strFilePath):
  picam2.start()
  time.sleep(2)
  picam2.capture_file(strFilePath)
  picam2.stop()

def submitPic(strFilePath,strToken,strFingerPrint):

  objFileIn = open(strFilePath,"rb")
  binBody = objFileIn.read()
  objFileIn.close()
  strMethod = "put"
  strURL = "https://connect.prusa3d.com/c/snapshot"
  dictHeader = {}
  dictHeader["Content-type"] = "image/jpeg"
  dictHeader["Fingerprint"] = strFingerPrint
  dictHeader["token"] = strToken
  WebRequest = requests.request(strMethod, strURL, data=binBody, timeout=iTimeOut, headers=dictHeader, verify=False)
  return WebRequest


def main():
  global picam2

  strVersion = "{0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
  strRealPath = os.path.realpath(sys.argv[0])

  print("This is a script to post pictures to prusa connect. "
          "This is running under Python Version {}".format(strVersion))
  print("Running from: {}".format(strRealPath))
  dtNow = time.strftime("%A %d %B %Y %H:%M:%S %Z")
  print("The time now is {}".format(dtNow))

  # fetching secrets in environment
  strToken = FetchEnv("PRUSATOKEN")
  if strToken == "":
    print("No API token, can't post without it.")
    sys.exit(9)

  strFingerPrint = FetchEnv("CAMFP")
  if strFingerPrint == "":
    print("No fingerprint, can't post without it.")
    sys.exit(9)

  strFilePath = FetchEnv("CAMPIC")
  if strFilePath == "":
    print("No filepath, can't work without it.")
    sys.exit(9)

  iInt = FetchEnv("CAMINT")
  if isInt(iInt):
    print("Interval specification of {} is valid".format(iInt))
    iInt=int(iInt)
  else:
    print("Invalid interval specification:'{}' defaulting to 5".format(iInt))
    iInt = 5

  strQuiet = FetchEnv("SILENT")
  if strQuiet.lower() == "true" or strQuiet.lower() == "yes":
     bQuiet = True
  else:
     bQuiet = False

  picam2 = Picamera2()
  camera_config = picam2.create_still_configuration()
  picam2.configure(camera_config)


  while True:
    takePic(strFilePath)
    strResponse = submitPic(strFilePath,strToken,strFingerPrint)
    if not bQuiet:
       print("picture posted with a response of {}".format(strResponse))
    time.sleep(iInt)

if __name__ == '__main__':
  main()
