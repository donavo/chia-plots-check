#! python
# -*- encoding: utf-8 -*-
# Author: son-vo
# Version:
# 0.1: Check health plot
# 0.1.1: Add feature move bad plot file to backup folder
# 0.1.2: Add feature auto delete bad plot file
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
badPlotFile = data['report_output_file1']
goodPlotFile = data['report_output_file2']
healthPoint = float(data['health_point'])
challenges = data['challenges']
autoDelete = data['auto_delete']
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

def doCheck(dir, badPlotFileOutput_, goodPlotFileOutput_):
    # Chia execute command
    plotTestCmd = ''
    # If not set plot_directories, check all
    if (not(dir and dir.strip())):
        plotTestCmd = [r"" + f'{chiaLocation}', "plots", "check", "-n", f'{challenges}']
    else:
        plotTestCmd = [r"" + f'{chiaLocation}', "plots", "check", "-n", f'{challenges}', "-g", f'{dir}']

    print ("Run command >>>", plotTestCmd)
    filePathLine = ''
    plotCount = 0
    res = sp.Popen(plotTestCmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    for line in res.stdout.readlines():
        if not line:
            break
        # Convert byte to String
        strLine = line.decode('utf-8').strip()
        if autoDelete == True:
            if isValidDirectory('E:/Temp/test/test.plot') == True:
                os.remove('E:/Temp/test/test.plot')
                print("%s has been deleted." % 'E:/Temp/test/test.plot')
        # Step1: Get file path
        strIndex = strLine.find('Testing plot')
        if strIndex != -1:
            filePathLine = strLine[strIndex:].replace('k=32', '').replace('[0m', '').strip()
        # Step2: Get Proofs
        strIndex = strLine.find('Proofs')
        if strIndex != -1:
            proofsLine = strLine[strIndex:].replace('k=32', '').replace('[0m', '').strip()
        if (strIndex != -1) and (filePathLine and filePathLine.strip()):
            point = float(proofsLine.split(',')[1].strip())
            plotFileName = filePathLine.split('Testing plot')[1].strip()
            if point < healthPoint:
                plotCount += 1
                print ("Found {0}: {1}".format(plotCount, plotFileName))
                print (proofsLine)
                # write plot file
                badPlotFileOutput_.write(plotFileName)
                badPlotFileOutput_.write('\n')
                # write Proofs
                badPlotFileOutput_.write(proofsLine)
                badPlotFileOutput_.write('\n')
                try:
                    if autoDelete == True:
                        if isValidDirectory(plotFileName) == True:
                            os.remove(plotFileName)
                            print("%s has been deleted." % plotFileName)
                    else:
                        if autoMove == True:
                            if isValidDirectory(moveToDir):
                                print('Move file {0} to {1}'.format(plotFileName, moveToDir))
                                plotNewPath = shutil.move(plotFileName, moveToDir)
                                print(plotNewPath)
                            else:
                                print('Directory %s is not exist' % moveToDir)
                except shutil.Error:
                    print('File Processing Error: %s' % plotFileName) 
            else:
                # write plot file
                goodPlotFileOutput_.write(plotFileName)
                goodPlotFileOutput_.write('\n')
                # write Proofs
                goodPlotFileOutput_.write(proofsLine)
                goodPlotFileOutput_.write('\n')
    
    print('Found {0} plots'.format(plotCount))
    badPlotFileOutput_.write('Found {0} plots'.format(plotCount))
    badPlotFileOutput_.write('\n')
    res.stdout.close()
################################################## Main function
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    if isValidDirectory(chiaLocation) == False:
        print('File %s is not exist' % chiaLocation)
        sys.exit(0)
    startTime = datetime.now()
    # Open file to output
    badPlotFileOutput_ = open(f'{badPlotFile}', 'w', encoding='UTF8')
    goodPlotFileOutput_ = open(f'{goodPlotFile}', 'w', encoding='UTF8')
    for dir in plotDirectories:
        if dir is None:
            doCheck('', badPlotFileOutput_, goodPlotFileOutput_)
        else:
            if isValidDirectory(dir):
                doCheck(dir, badPlotFileOutput_, goodPlotFileOutput_)
            else:
                print('Directory %s is not exist' % dir)
    badPlotFileOutput_.close()
    durationTime()