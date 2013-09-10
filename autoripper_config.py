
import os

#Variables that will reference binaries
MAKEMKVCON = '/usr/bin/makemkvcon'         #this was tested with 1.8.4 beta
HANDBRAKE_CLI = '/usr/bin/HandBrakeCLI'    #tested with 0.9.9

list_of_bins = [ MAKEMKVCON, HANDBRAKE_CLI]

#Variables that will reference Storage Locations
RIP_LOCATION = r'/home/mediacenter/rips/'
CONVERT_LOCATION = r'/home/mediacenter/converts/'
OUTPUT_MOVIE_LOCATION = r'/home/mediacenter/exthdd1/Movies/'
MOVIE_LOCATION = [ OUTPUT_MOVIE_LOCATION ]    #This way if you have multiple locations it will check them all

list_of_dirs = [ RIP_LOCATION, CONVERT_LOCATION, OUTPUT_MOVIE_LOCATION]

#Variables that will reference hardware
BLURAY_DEVICE = r'/dev/sr0'                   #This should be the default location for your bluray device
MAKEMKV_DISC_NUM = BLURAY_DEVICE[-1]          #This is the cdrom drive number

list_of_devs = [ BLURAY_DEVICE]

#Need to put error checking to make sure directories and files exist

def dirExist(listOfDirectories):
    for directory in ListOfDirectories:
        if not os.path.isdir(directory):
            os.makedirs(directory)

def pathExist(listOfPaths, isFile=True):
    for path in listOfPaths:
        if not os.path.exists(path):
            if not isFile:
                print 'Path does not exists for %s' % path
                return False
            
dirExist(list_of_dirs)
dirExist(MOVIE_LOCATION)

if pathExist(list_of_bins) and pathExist(list_of-dirs):
    continue
else:
    pass  #Need to find a clean way to bail
    
