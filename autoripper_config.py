import os
from glob import glob

HOME = os.path.expanduser('~')

##########################[ MODIFY THESE SETTINGS TO FIT YOUR SETUP ]####################################

#Variables that will reference binaries
MAKEMKVCON = '/usr/bin/makemkvcon'         #this was tested with 1.8.4 beta
HANDBRAKE_CLI = '/usr/bin/HandBrakeCLI'    #tested with 0.9.9


#Variables that will reference Storage Locations
RIP_LOCATION = HOME + r'/rips/'
CONVERT_LOCATION = HOME + r'/converts/'
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

'''Functions to prevent operator error, hopefully'''
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

'''Functions that make my life easier'''
def sleep(seconds=5):
    return time.sleep(seconds)
    
    
dirExist(list_of_dirs)
dirExist(MOVIE_LOCATION)

    
