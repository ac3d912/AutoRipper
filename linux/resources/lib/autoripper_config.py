#!/usr/bin/python

import os
import time
from glob import glob

HOME = os.path.expanduser('~')

##########################[ MODIFY THESE SETTINGS TO FIT YOUR SETUP ]####################################

#Variables that will reference binaries
MAKEMKVCON = '/usr/bin/makemkvcon'         #this was tested with 1.8.4 beta
HANDBRAKE_CLI = '/usr/bin/HandBrakeCLI'    #tested with 0.9.9


#Variables that will reference Storage Locations
RIP_LOCATION = HOME + r'/exthdd2/autoripper/rips/'
CONVERT_LOCATION = HOME + r'/exthdd2/autoripper/converts/'
OUTPUT_MOVIE_LOCATION = HOME + r'/exthdd1/Movies/'
MOVIE_LOCATION = [ OUTPUT_MOVIE_LOCATION ]    #This way if you have multiple locations it will check them all


#Variables that will reference hardware
BLURAY_DEVICE = r'/dev/sr0'                   #This should be the default location for your bluray device
MAKEMKV_DISC_NUM = BLURAY_DEVICE[-1]          #This is the cdrom drive number

#Variables that will reference misc software
XBMC_MOVIE_DB = glob(HOME + r'/.xbmc/userdata/Database/MyVideos*.db')[0]

###############################[ DON'T EDIT ANYTHING BELOW THIS ]#########################################

list_of_bins = [ MAKEMKVCON, HANDBRAKE_CLI ]
list_of_dirs = [ RIP_LOCATION, CONVERT_LOCATION, OUTPUT_MOVIE_LOCATION ]
list_of_devs = [ BLURAY_DEVICE ]

timeStamp = []

'''Functions to prevent operator error, hopefully'''
def dirExist(listOfDirectories):
    for directory in listOfDirectories:
        if not os.path.isdir(directory):
            os.makedirs(directory)

def pathExist(listOfPaths, isFile=True):
    for path in listOfPaths:
        if not os.path.exists(path):
            if not isFile:
                print 'Path does not exists for %s' % path
                return False
    return True

'''Functions that make my life easier'''
def sleep(seconds=5):
    return time.sleep(seconds)
    
def dbWrite(msg, error=False):
    print (msg)
    
def movieTime(code, name=None):
    #0 start
    #1 means stop
    #2 means print dif
    global timeStamp
    
    if code == 0: #start
        timeStamp = [time.time()]   
    elif code == 1: #stop
        if len(timeStamp) == 1:
            timeStamp.append(time.time())
        else:
            return False
    elif code == 2: #print
        if len(timeStamp) == 2:
            startTime = timeStamp[0]
            stopTime = timeStamp[1]
            
            diffTime = stopTime - startTime
            convertToMins = diffTime / 60
            
            results = 'Time to process %.2f mins' %convertToMins
            
            if name is not None:
                results += ' with %s' %name
            
            return results
        
         
dirExist(list_of_dirs)
dirExist(MOVIE_LOCATION)