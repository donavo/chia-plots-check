#! python
# -*- encoding: utf-8 -*-
# Author: son-vo
# Version: 0.1
##################################################
# Check and output health of plots
# Requirement: install pyyaml
# python3 -m pip install --user pyyaml
# Syntax:
# py CheckHealthPlot.py
# or python3 CheckHealthPlot.py
##################################################
import yaml
from yaml.loader import SafeLoader
from time import sleep
from datetime import datetime
import signal
import sys
import os
import subprocess as sp

try:
    # Open the file and load the file
    with open('config.yaml') as f:
        data = yaml.load(f, Loader = SafeLoader)
        #print(data['chia_location'])
except yaml.YAMLError:
    print("Error in configuration file:")
    sys.exit(0)

# Get config params
chiaLocation = data['chia_location']
plotPath = data['plots_path']
outputFile = data['report_output_file']
healthPoint = float(data['health_point'])
# Chia execute command
plotTestCmd = [r"" + f'{chiaLocation}' + "", "plots", "check", "-g", f'{plotPath}']
################################################## Function to catch ctrl-c
# Handle ctr-c
def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    durationTime()
    sys.exit(0)

################################################## Function to catch ctrl-c => End
def durationTime():
    duration = datetime.now() - startTime
    print('Run in', duration)
    print("*****************************")

################################################## Main function
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    startTime = datetime.now()
    # print (plotTestCmd)
    res = sp.Popen(plotTestCmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    # Open file to output
    outputFile_ = open(f'{outputFile}', 'w', encoding='UTF8')
    plotFilePath = ''
    for line in res.stdout.readlines():
        if not line:
            break
        # Convert byte to String
        s = line.decode('utf-8').strip()
        # Step1: Get file path
        strIndex = s.find('Testing plot')
        if strIndex != -1:
            plotFilePath = s[strIndex:].replace('k=32', '').replace('[0m', '').strip()
        # Step2: Get Proofs
        strIndex = s.find('Proofs')
        if strIndex != -1:
            proofsLine = s[strIndex:].replace('k=32', '').replace('[0m', '').strip()
            point = float(proofsLine.split(',')[1].strip())
            if point < healthPoint:
                print (plotFilePath)
                print (proofsLine)
                # write plot file
                outputFile_.write(plotFilePath)
                outputFile_.write('\n')
                # write Proofs
                outputFile_.write(proofsLine)
                outputFile_.write('\n')
                plotFilePath = ''
    outputFile_.close()
    res.stdout.close()
    durationTime()