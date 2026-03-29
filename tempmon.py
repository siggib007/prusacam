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
import requests
import json

# Define few Defaults
iLogLevel = 4  # How much logging should be done. Level 10 is debug level, 0 is none
iTimeOut = 180  # Max time in seconds to wait for network response
iMinQuiet = 2  # Minimum time in seconds between API calls
strURL = "https://s2313682.eu-fsn-3.betterstackdata.com/metrics"
strHBURL = "https://uptime.betterstack.com/api/v1/heartbeat/nFLF1mtJNxFUKRowLML4HJF6"

if sys.version_info[0] > 2:
    import urllib.parse as urlparse
    # The following line surpresses a warning that we aren't validating the HTTPS certificate
    requests.urllib3.disable_warnings()
else:
   print("This script is only supported on python 3")
   sys.exit(9)

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

def Convert2OpenMetricGauge(dictPayloads):
    """
    Transform a dictionary of metrics into OpenMetrics format, type Gauge.

    Parameters:
      dictPayloads: Dictionary with metric names as keys and numerical values

    Returns:
      List of dictionaries in OpenMetrics format

    Example:
      >>> BuildMetricsPayload({"temperature": 45.2, "clock_speed": 1800})
      [
          {"name": "temperature", "gauge": {"value": 45.2}},
          {"name": "clock_speed", "gauge": {"value": 1800}}
      ]
    """
    listMetrics = []
    for metric_name, metric_value in dictPayloads.items():
        dictMetric = {
            "name": metric_name,
            "gauge": {
                "value": metric_value
            }
        }
        listMetrics.append(dictMetric)
    return listMetrics

def SubmitMetric(dictPayload):
  strMethod = "post"

  #print("Submitting metric to server:{}".format(json.dumps(dictPayload)))
  dictHeader = {}
  dictHeader["Content-type"] = "application/json"
  dictHeader["Authorization"] = "Bearer " + strToken
  WebRequest = requests.request(strMethod, strURL, json=dictPayload, timeout=iTimeOut, headers=dictHeader, verify=False)

  return WebRequest

def main():
  global strToken


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
  
  strOutDir  = strBaseDir + "Out/"
  if strOutDir[-1:] != "/":
    strOutDir += "/"

  iLoc = sys.argv[0].rfind(".")

  if not os.path.exists (strOutDir) :
    os.makedirs(strOutDir)
    print("\nPath '{0}' for output files didn't exists, so I create it!\n".format(strOutDir))

  strScriptName = os.path.basename(sys.argv[0])
  iLoc = strScriptName.rfind(".")
  strFilePath = strOutDir + strScriptName[:iLoc] + ISO + ".csv"
  if objArgs.file_name is not None:
     strFilePath=objArgs.file_name



  # fetching secrets in environment
  strToken = FetchEnv("TOKEN")
  if strToken == "":
    print("No API token, can't post without it.")
    sys.exit(9)


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
    dictPayload = {}
    dictPayload["temperature"] = fTempiture
    dictPayload["clock_speed"] = iClockSpeed
    dictPayload["throttled"] = bThrottled
    lstMetrics = Convert2OpenMetricGauge(dictPayload)
    WebResponse = SubmitMetric(lstMetrics)

    strOut = "{},{},{},{}\n".format(strCurTime,fTempiture,iClockSpeed,bThrottled)
    if not objArgs.silent:
      print(strOut, end="")
      print("Response from server: {} {}".format(WebResponse.status_code, WebResponse.text))
    objFile.write(strOut)
    objFile.flush()
    WebRequest = requests.request("HEAD", strHBURL, timeout=iTimeOut, verify=False)
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