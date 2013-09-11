#!/usr/bin/python

import subprocess
import os
import re
import shutil
import sqlite3 as sql
import time

from glob import glob

from resources.lib.autoripper_config import *

def convert_with_handbrake(movieLocation):
    '''
        I figure you don't NEED this unless you want the compression factor.  DVD's will take a max of 9 gigs and since I am a quality whore
        I am going to keep them as close to normal as possible.  Will leave an option for you to override if you feel like it.
    '''
    
    settings = {    'input'         :   movieLocation,
                    'output'        :   CONVERT_LOCATION + os.path.split(movieLocation)[-1],
                    'backupAudio'   :   'ac3,dts,dtshd',
                    'fallbackAudio' :   'ffac3',
                    'videoEncode'   :   'x264',
                    'videoQuality'  :   '20',
                    'advancedEncode':   'level=4.1:ref=4:b-adapt=2:direct=auto:me=umh:subq=8:rc-lookahead=50:psy-rd=1.0,0.15:deblock=-1,-1:vbv-bufsize=30000:vbv-maxrate=40000:slices=4'            
               }
    
    tmp =  subprocess.call([ HANDBRAKE_CLI, '-i', settings['input'], '-o', settings['output'], '-m', '-E', 'copy', '--audio-copy-mask', settings['backupAudio'], '--audio-fallback', settings['fallbackAudio'], '-e', settings['videoEncode'], '-q', settings['videoQuality'], '-x', settings['advancedEncode']], stdout=subprocess.PIPE)
    
    if tmp == 0:
        os.remove(movieLocation)    #No need to keep the ripped version if this worked.

    return True
    
    
def rip_with_makemkv(movieName):
    '''
        I am going to make some assumptions for round 1.  I am going to assume you want an english only disk
        without subs.  I am going to remove all 3D and special tracks.
    '''

    settings = {    'cache'            :    1024,
                    'audioSettings'    :    '-sel:all,+sel:audio&(eng),-sel:(havemulti),-sel:mvcvideo,-sel:special,+sel:lossless', #dont know how to implement this one yet
                    'minLength'        :    3601,
                    'discAccess'       :    'true'  #examples are all lowercase
                }
             
    #To get disk info
    discInfo = subprocess.check_output([ MAKEMKVCON, '-r', 'info', 'disc:%s' % MAKEMKV_DISC_NUM ])
    
    if re.search('"Failed to open disc"', discInfo):
        return False
    
    print '\tGot disc info'
    #To rip disk and eject once finished
    
    subprocess.call([ MAKEMKVCON, '--minlength=%d' %settings['minLength'], '-r', '--decrypt', '--directio=%s' %settings['discAccess'], 'mkv', 
                            'disc:%s' % MAKEMKV_DISC_NUM, 'all', RIP_LOCATION], stdout=subprocess.PIPE)
    
    tmp = subprocess.call([ 'eject', '-s', BLURAY_DEVICE ])
    
    if tmp == 1:
        cleanup_bad_jobs()
        return False

    '''[ TO DO ] Currently I am going to assume that the first track is the track we want, I will add better control once 
    I figure out all the options to makemkvcon'''
    
    ripMovieName = glob(RIP_LOCATION + '*t00.mkv')[0]
    
    return ripMovieName
    
    
def check_if_owned(movieLabel): #Need help
    '''[ TO DO ] Need to find a way to take CDROM Label and scrap a site to get the movie title.'''

    return movieLabel    #Doing this to make it work until I figure out how to get a movie title from the disc.
    
    '''Below this line works.  Will enable once I can find out how to get the movie title from the disc.'''
    
    #Going to do a simple sql query for the Movie database in XBMC and comparing it to the title we have
    con = sql.connect(XBMC_MOVIE_DB)
    
    cur = con.cursor()
    cur.execute("SELECT c00 FROM movie")
    movieList = cur.fetchall()
    
    found = False
    
    for movieTuple in movieList:
        movie = movieTuple[0]
        
        if movieTitle == movie:
            found = True
            break
    
    cur.close()
    con.close()
    
    return found
        
    
def cleanup_bad_jobs():
    dirsToCheck = [ RIP_LOCATION, CONVERT_LOCATION ] #May want to add other cleanup locations

    for directory in dirsToCheck:
        filesToDelete = [ f for f in os.listdir(directory) ]
    
        for file in filesToDelete:
            os.remove(directory + file)
    
    return True
    
    
def cd_tray_watcher(cdTrayInfo):
    media = {   'timeStamp'     :   None,
                'label'         :   None,
                'type'          :   None,
                'serial'        :   None,
                'by-id'         :   None
            }
            
    if cdTrayInfo is None:
        timeStamp = None
    else:
        timeStamp = cdTrayInfo
    
    while True:
        tmp = subprocess.check_output([ 'udisks', '--show-info', BLURAY_DEVICE ])
        
        if not re.search('has media:\W+1',tmp): #Checks to see if drive is empty
            sleep()    #This way we are not spiking CPU usage
            continue
        
        '''[ TO DO ] Can clean the regex's up a lot to prevent having to use greedy flags, will do later'''
        media['timeStamp'] = re.findall('has media:\W+\d\W(.*?)\n', tmp)[0]
        media['label'] = re.findall('label:\W+(.*?)\n', tmp)[0]
        media['type'] = re.findall('\W\W+media:\W+(.*?)\n', tmp)[0]
        media['serial'] = re.findall('\W+serial:\W+(.*?)\n', tmp)[0]
        media['by-id'] = re.findall('\W+by-id:\W+(.*?)\n', tmp)[0]
        
        if not media['type'] in [ 'optical_bd', 'optical_dvd']:
            sleep()    #This way we are not spiking CPU usage
            continue
        
        if timeStamp == media['timeStamp']:
            sleep()    #This way we are not spiking CPU usage
            continue
        
        return media
        
    
def program_watcher(): 
    cdTrayInfo = None
    
    while True: 
        cleanup_bad_jobs()  
        movieInfo = cd_tray_watcher(cdTrayInfo)
        cdTrayInfo = movieInfo['timeStamp']
        
        if not check_if_owned(movieInfo['label']):
            continue
        
        mkvMoviePath = rip_with_makemkv(movieInfo['label'])
        
        if not mkvMoviePath:
            continue
        
        if movieInfo['type'] == 'optical_bd' :
            moviePath = convert_with_handbrake(mkvMoviePath)
            
            if not moviePath:
                shutil.move(moviePath, OUTPUT_MOVIE_LOCATION)
        
        else:
            shutil.move(mkvMoviePath, OUTPUT_MOVIE_LOCATION)
        

if __name__ == '__main__':
    if pathExist(list_of_bins) and pathExist(list_of_dirs):
        program_watcher()
        
    else:
        print 'failed to find paths.  Please check autoripper_config to make sure things are set correctly.'
    

