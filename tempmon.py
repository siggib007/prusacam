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
tLastCall = 0
iTotalSleep = 0
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

def CleanExit(strCause):
  """
  Handles cleaning things up before unexpected exit in case of an error.
  Things such as closing down open file handles, open database connections, etc.
  Logs any cause given, closes everything down then terminates the script.
  Parameters:
    Cause: simple string indicating cause of the termination, can be blank
  Returns:
    nothing as it terminates the script
  """
  LogEntry("{} is exiting abnormally on {}: {}".format(
    strScriptName, strScriptHost, strCause), 0)
  if objFileIn:
    objFileIn.close()
    LogEntry("objFileIn closed")

  objLogOut.close()
  print("objLogOut closed")

  sys.exit(9)

def LogEntry(strMsg, iMsgLevel=0, bAbort=False):
  """
  This handles writing all event logs into the appropriate log facilities
  This could be a simple text log file, a database connection, etc.
  Needs to be customized as needed
  Parameters:
    Message: Simple string with the event to be logged
    iMsgLevel: How detailed is this message, debug level or general. Will be matched against Loglevel
    Abort: Optional, defaults to false. A boolean to indicate if CleanExit should be called.
  Returns:
    Nothing
  """
  if iVerbose > iMsgLevel:
    strTimeStamp = time.strftime("%m-%d-%Y %H:%M:%S")
    objLogOut.write("{0} : {1}\n".format(strTimeStamp, strMsg))
    print(strMsg)
  else:
    if bAbort:
      strTimeStamp = time.strftime("%m-%d-%Y %H:%M:%S")
      objLogOut.write("{0} : {1}\n".format(strTimeStamp, strMsg))

  if bAbort:
    CleanExit("")

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

def MakeAPICall(strURL, dictHeader, strMethod, dictPayload="", objFiles=[], strUser="", strPWD=""):
  """
  Handles the actual communication with the API, has a backoff mechanism
  MinQuiet defines how many seconds must elapse between each API call.
  Sets a global variable iStatusCode, with the HTTP code returned by the API (200, 404, etc)
  Parameters:
    strURL: Simple String. API EndPoint to call
    dictHeader: Dictionary object with the header to pass along with the call
    strMethod: Simple string. Call method such as GET, PUT, POST, etc
    dictPayload: Optional. Any payload to send along in the appropriate structure and format
    objFiles: Optional. List of files (full absolute paths) or multipart object to be uploaded, if any
    User: Optional. Simple string. Username to use in basic Auth
    Password: Simple string. Password to use in basic auth
  Return:
    Returns a tupple of single element dictionary with key of Success,
    plus a list with either error messages or list with either error messages
    or result of the query, list of dictionaries..
    ({"Success":True/False}, [dictReturn])
  """
  global tLastCall
  global iTotalSleep
  global iStatusCode

  fTemp = time.time()
  fDelta = fTemp - tLastCall
  LogEntry("It's been {} seconds since last API call".format(fDelta), 4)
  if fDelta > iMinQuiet:
    tLastCall = time.time()
  else:
    iDelta = int(fDelta)
    iAddWait = iMinQuiet - iDelta
    LogEntry("It has been less than {} seconds since last API call, "
              "waiting {} seconds".format(iMinQuiet, iAddWait), 4)
    iTotalSleep += iAddWait
    time.sleep(iAddWait)

  strErrCode = ""
  strErrText = ""
  dictReturn = {}

  LogEntry("Doing a {} to URL: {}".format(strMethod, strURL), 1)
  try:
    if strMethod.lower() == "head":
      WebRequest = requests.request("HEAD", strURL, timeout=iTimeOut, verify=False, proxies=dictProxies, headers=dictHeader)
    if strMethod.lower() == "get":
      if strUser != "":
        LogEntry(
            "I have none blank credentials so I'm doing basic auth", 3)
        WebRequest = requests.get(strURL, timeout=iTimeOut, headers=dictHeader,
                                  auth=(strUser, strPWD), verify=False, proxies=dictProxies)
      else:
        LogEntry("credentials are blank, proceeding without auth", 3)
        WebRequest = requests.get(
            strURL, timeout=iTimeOut, headers=dictHeader, verify=False, proxies=dictProxies)
      LogEntry("get executed", 4)
    if strMethod.lower() == "post":
      if dictPayload:
        dictTmp = dictPayload.copy()
        if "password" in dictTmp:
            dictTmp["password"] = dictTmp["password"][:2]+"*********"
        if "clientSecret" in dictTmp:
            dictTmp["clientSecret"] = dictTmp["clientSecret"][:2]+"*********"
        if strUser != "":
          LogEntry("I have none blank credentials so I'm doing basic auth", 3)
          LogEntry("with user auth, payload of: {} and files object of {}".format(dictTmp,objFiles), 4)
          WebRequest = requests.post(strURL, json=dictPayload, timeout=iTimeOut,
                                      headers=dictHeader, auth=(strUser, strPWD),
                                      verify=False, proxies=dictProxies,files=objFiles)
        else:
          LogEntry("credentials are blank, proceeding without auth", 3)
          LogEntry("with payload of: {} and files object of {}".format(dictTmp,objFiles), 4)
          WebRequest = requests.post(
              strURL, json=dictPayload, timeout=iTimeOut, headers=dictHeader,
              files=objFiles, verify=False, proxies=dictProxies)
      else:
        LogEntry("No payload, doing a simple post", 3)
        LogEntry("with files object of: {}".format(objFiles), 4)
        WebRequest = requests.post(
            strURL, headers=dictHeader, verify=False, proxies=dictProxies, files=objFiles)
      LogEntry("post executed", 4)
    if strMethod.lower() == "delete":
      WebRequest = requests.delete(strURL, headers=dictHeader, verify=False, proxies=dictProxies)

  except Exception as err:
    dictReturn["url"] = strURL
    dictReturn["condition"] = "Issue with API call"
    dictReturn["errormsg"] = err
    return ({"Success": False}, [dictReturn])

  if isinstance(WebRequest, requests.models.Response) == False:
    LogEntry("response is unknown type", 1)
    strErrCode = "ResponseErr"
    strErrText = "response is unknown type"

  LogEntry("call resulted in status code {}".format(
    WebRequest.status_code), 3)
  iStatusCode = int(WebRequest.status_code)

  if not 200 <= iStatusCode <= 299:
    print("call resulted in status code {}".format(WebRequest.status_code))
    strErrCode += str(iStatusCode)
    strErrText += WebRequest.text
    LogEntry("HTTP Error: {}".format(iStatusCode), 3)
    LogEntry("Response: {}".format(WebRequest.content), 4)
  if strErrCode != "":
    dictReturn["url"] = strURL
    dictReturn["condition"] = "problem with your request"
    dictReturn["errcode"] = strErrCode
    dictReturn["errormsg"] = strErrText
    return ({"Success": False}, [dictReturn])
  else:
    if "<html>" in WebRequest.text[:99] or WebRequest.text == "":
      if WebRequest.text == "":
        return ({"Success": True},"")
      else:
        return ({"Success": False}, WebRequest.text[:99])
    try:
      return ({"Success": True}, WebRequest.json())
    except Exception as err:
      dictReturn["condition"] = "failure converting response to jason"
      dictReturn["errormsg"] = err
      dictReturn["errorDetail"] = "Here are the first 199 character of the response: {}".format(
          WebRequest.text[:199])
      return ({"Success": False}, [dictReturn])

def SubmitMetric(dictPayload):
  strMethod = "post"

  #print("Submitting metric to server:{}".format(json.dumps(dictPayload)))
  dictHeader = {}
  dictHeader["Content-type"] = "application/json"
  dictHeader["Authorization"] = "Bearer " + strToken
  WebRequest = MakeAPICall(strURL,dictHeader,strMethod,dictPayload)
  #WebRequest = requests.request(strMethod, strURL, json=dictPayload, timeout=iTimeOut, headers=dictHeader, verify=False)

  return WebRequest

def main():
  global strToken
  global bQuiet
  global objLogOut
  global iVerbose
  global dictProxies

  objParser = argparse.ArgumentParser(description="Raspberry Pi Monitor")
  objParser.add_argument("--silent", dest="silent",
                      action="store_true", help="only output to file, not to screen")
  objParser.add_argument("--sleep", dest="sleep_time", type=int,
                      help="Number of seconds to sleep inbetween checks, default is 60")
  objParser.add_argument("--filename", dest="file_name", type=str, help="Output file name, "
                         "defaults to {scriptname}-iso-date.csv in the script directory")
  objParser.add_argument("-v", "--verbosity", action="count", default=1, help="Verbose output, vv level 2 vvvv level 4")
  objParser.add_argument("-x", "--proxy", type=str, help="Proxy to use for API calls")

  objArgs = objParser.parse_args()
  if objArgs.sleep_time is not None:
    iSleepSec = objArgs.sleep_time
  else:
     iSleepSec = 60
  iVerbose = objArgs.verbosity

  ISO = time.strftime("-%Y-%m-%d")
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

  strLogDir  = strBaseDir + "Logs/"
  if strLogDir[-1:] != "/":
    strLogDir += "/"

  iLoc = sys.argv[0].rfind(".")

  if not os.path.exists (strLogDir) :
    os.makedirs(strLogDir)
    print("\nPath '{0}' for log files didn't exists, so I create it!\n".format(strLogDir))

  strScriptName = os.path.basename(sys.argv[0])
  iLoc = strScriptName.rfind(".")
  strFilePath = strOutDir + strScriptName[:iLoc] + ISO + ".csv"
  if objArgs.file_name is not None:
     strFilePath=objArgs.file_name

  strLogFile = strLogDir + strScriptName[:iLoc] + ISO + ".log"
  objLogOut = open(strLogFile, "a", 1)


  # fetching secrets in environment
  strToken = FetchEnv("TOKEN")
  if strToken == "":
    LogEntry("No API token, can't post without it.")
    sys.exit(9)
  dictProxies = {}
  if FetchEnv("PROXY") is not None:
    strProxy = os.getenv("PROXY")
  if objArgs.proxy is not None:
    strProxy = objArgs.proxy
  if strProxy is not None:
    dictProxies["http"] = strProxy
    dictProxies["https"] = strProxy
    LogEntry("Proxy has been configured for {}".format(strProxy))
  else:
    LogEntry("No proxy has been configured")

  bQuiet = objArgs.silent
  if bQuiet:
    iVerbose = 0
  else:
    LogEntry("This is a script to raspberrypi cpu stats. "
            "This is running under Python Version {}".format(strVersion))
    LogEntry("Running from: {}".format(strRealPath))
    dtNow = time.strftime("%A %d %B %Y %H:%M:%S %Z")
    LogEntry("Script started at {}".format(dtNow))
    LogEntry("Output written to {}".format(strFilePath))

  objFile = open(strFilePath, mode="a", buffering=1, encoding="utf-8")
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

    strOut = "{},{},{},{}".format(strCurTime,fTempiture,iClockSpeed,bThrottled)
    if not bQuiet:
      LogEntry(strOut)
      LogEntry("Response from server: {}".format(WebResponse))
    objFile.write(strOut+"\n")
    objFile.flush()
    WebRequest = MakeAPICall(strHBURL,{},"HEAD")
    #WebRequest = requests.request("HEAD", strHBURL, timeout=iTimeOut, verify=False)
    if bQuiet:
      time.sleep(iSleepSec)
    else:
      LogEntry("Response from heartbeat server: {}".format(WebResponse))
      strResp = timed_input("Sleeping for {} seconds, enter q to exit ...".format(iSleepSec),iSleepSec)
      if isinstance(strResp,str):
        if len(strResp) > 0:
            if strResp.lower()[0] == "q":
              bContinue = False




if __name__ == "__main__":
  main()