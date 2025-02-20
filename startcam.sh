#!/bin/bash
#exec > /home/siggib/prusacam/cam.log 2>&1
#set -x

export PRUSATOKEN=Pf3Wid2WOjGjaWRFs30c
export CAMFP=db019aca-826a-4211-bb8d-5481ed352e07
export CAMPIC=/tmp/prusaimg.jpg
export CAMINT=5
export SILENT=true
python3 /home/siggib/prusacam/prusacam.py
# python3 /home/siggib/prusacam/tempmon.py --sleep 120 --silent