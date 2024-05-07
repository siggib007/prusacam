'''
Script that takes pictures using picamera2
then posts them to Prusa connect

Author Siggi Bjarnason 07 may 2024
Copyright 2023 Siggi Bjarnason

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
  picam2 = Picamera2()
  camera_config = picam2.create_still_configuration()
  picam2.configure(camera_config)
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

  strScriptName = os.path.basename(sys.argv[0])
  strVersion = "{0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
  strScriptHost = platform.node().upper()
  strRealPath = os.path.realpath(sys.argv[0])

  print("This is a script to test if a URL responds via proxy. "
          "This is running under Python Version {}".format(strVersion))
  print("Running from: {}".format(strRealPath))
  dtNow = time.strftime("%A %d %B %Y %H:%M:%S %Z")
  print("The time now is {}".format(dtNow))

  # fetching secrets in environment
  strToken = FetchEnv("APIKEY")
  if strToken == "":
    print("No API token, can't post without it.")
    sys.exit(9)

  strFingerPrint = FetchEnv("FP")
  if strFingerPrint == "":
    print("No fingerprint, can't post without it.")
    sys.exit(9)

  strFilePath = FetchEnv("FILE")
  if strFilePath == "":
    print("No filepath, can't work without it.")
    sys.exit(9)

  takePic(strFilePath)
  print(submitPic(strFilePath,strToken,strFingerPrint))

if __name__ == '__main__':
  main()
