#! python
# -*- encoding: utf-8 -*-
# Author: son-vo
# Version:
# 0.1: Check health plot
# 0.1.1: Add feature move plot file to backup folder
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
import shutil

def isValidDirectory(directoryPath):
    # Checking if the directory exists or not
    if os.path.exists(directoryPath):
        # Checking if the directory is empty or not
        #if len(os.listdir(directoryPath)) == 0:
        #    return False
        return True
    else:
        if os.path.isfile(directoryPath):
            return True
        return False

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
plotDirectories = data['plot_directories']
outputFile = data['report_output_file']
healthPoint = float(data['health_point'])
autoMove = data['auto_move']
moveToDir = data['move_to_directory']
################################################## Function to catch ctrl-c
# Handle ctr-c
def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    durationTime()
    sys.exit(0)

################################################## Function to catch ctrl-c => End
def durationTime():
    duration = datetime.now() - startTime
    print('Total time >>>', duration)
    print("*****************************")

def doCheck(dir, outputFile_):
    # Chia execute command
    plotTestCmd = ''
    # If not set plot_directories, check all
    if (not(dir and dir.strip())):
        plotTestCmd = [r"" + f'{chiaLocation}', "plots", "check"]
    else:
        plotTestCmd = [r"" + f'{chiaLocation}', "plots", "check", "-g", f'{dir}']

    print ("Testing directory >>>", dir)
    plotFilePath = ''
    plotCount = 0
    res = sp.Popen(plotTestCmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    for line in res.stdout.readlines():
        if not line:
            break
        # Convert byte to String
        strLine = line.decode('utf-8').strip()
        # Step1: Get file path
        strIndex = strLine.find('Testing plot')
        if strIndex != -1:
            plotFilePath = strLine[strIndex:].replace('k=32', '').replace('[0m', '').strip()
        # Step2: Get Proofs
        strIndex = strLine.find('Proofs')
        if strIndex != -1:
            proofsLine = strLine[strIndex:].replace('k=32', '').replace('[0m', '').strip()
            point = float(proofsLine.split(',')[1].strip())
            if point < healthPoint:
                plotCount += 1
                print ("#{0}: {1}".format(plotCount, plotFilePath))
                print (proofsLine)
                # write plot file
                outputFile_.write(plotFilePath)
                outputFile_.write('\n')
                # write Proofs
                outputFile_.write(proofsLine)
                outputFile_.write('\n')
                try:
                    if autoMove == True:
                        if isValidDirectory(moveToDir):
                            plotFile = plotFilePath.split('Testing plot')[1].strip()
                            print('Move file {0} to {1}'.format(plotFile, moveToDir))
                            plotNewPath = shutil.move(plotFile, moveToDir)
                            print(plotNewPath)
                        else:
                            print('Directory %s is not exist' % moveToDir)
                except shutil.Error:
                    print('Error to remove file %s' % plotFile) 
                plotFilePath = ''
    print('Found {0} plots in {1}'.format(plotCount, dir))
    res.stdout.close()
################################################## Main function
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    if isValidDirectory(chiaLocation) == False:
        print('File %s is not exist' % chiaLocation)
        sys.exit(0)
    startTime = datetime.now()
    # Open file to output
    outputFile_ = open(f'{outputFile}', 'w', encoding='UTF8')
    for dir in plotDirectories:
        if isValidDirectory(dir):
            doCheck(dir, outputFile_)
        else:
            print('Directory %s is not exist' % dir)
    outputFile_.close()
    durationTime()