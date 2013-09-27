#!/usr/bin/python

import subprocess
import os.path
import re
import shutil
import sqlite3 as sql
import dbus
import gobject

from glob import glob
from resources.lib.autoripper_config import *
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

sqlList = []

def disk_already_checked(diskLabel, checkOnly=True):
    global sqlList
    
    if diskLabel in sqlList:
        return True
    else:
        
        if not checkOnly:
            dbWrite('Adding %s to database' %diskLabel)
            sqlList.append(diskLabel)
        
        return False
   
   
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
                    'advancedEncode':   'level=4.1',
                    'audioTrack'    :   '1',
                    'x264-profile'  :   'high'
               }

    
    movieTime(0)
    tmp =  subprocess.call([ HANDBRAKE_CLI, '-i', settings['input'], '-o', settings['output'], '--markers', '--audio', settings['audioTrack'], 
                            '--aencoder', 'copy', '--audio-copy-mask', settings['backupAudio'], '--audio-fallback', settings['fallbackAudio'], 
                            '--encoder', settings['videoEncode'], '--x264-profile', settings['x264-profile'], '--two-pass', '--turbo'])
    
    if tmp == 0:
        os.remove(movieLocation)    #No need to keep the ripped version if this worked.
    else:
        dbWrite('Failed to convert via handbrake', True)
        return False
    
    movieTime(1)
    dbWrite(movieTime(2, 'handbrake'))
    
    return CONVERT_LOCATION + os.path.split(movieLocation)[-1]
    
    
def rip_with_makemkv(movieName):
    '''
        I am going to make some assumptions for round 1.  I am going to assume you want an english only disk
        without subs.  I am going to remove all 3D and special tracks.
    '''
    
    settings = {    'cache'            :    1024,
                    'minLength'        :    3601,
                    'discAccess'       :    'true'  #examples are all lowercase
                }
             
    #To get disk info
    discInfo = subprocess.check_output([ MAKEMKVCON, '-r', 'info', 'disc:%s' % MAKEMKV_DISC_NUM ])
    print discInfo
    
    if re.search('"Failed to open disc"', discInfo):
        return False
    
    #To rip disk and eject once finished
    movieTime(0)
    subprocess.call([ MAKEMKVCON, '--minlength=%d' %settings['minLength'], '-r', '--decrypt', '--directio=%s' %settings['discAccess'], 'mkv', 
                            'disc:%s' % MAKEMKV_DISC_NUM, 'all', RIP_LOCATION], stdout=subprocess.PIPE)
    movieTime(1)
    dbWrite(movieTime(2, 'makemkv'))
    tmp = subprocess.call([ 'eject', '-s', BLURAY_DEVICE ])
    
    if tmp == 1:
        dbWrite('Failed to rip with makemkv', True)
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
        
        if movieLabel == movie:
            found = True
            break
    
    cur.close()
    con.close()
    
    return found
        
    
def cleanup_bad_jobs():
    dirsToCheck = [ RIP_LOCATION, CONVERT_LOCATION ] #May want to add other cleanup locations
    for directory in dirsToCheck:
        filesToDelete = [ f for f in os.listdir(directory) ]
    
        for file_name in filesToDelete:
            dbWrite('Deleting ' + directory + file_name)
            os.remove(directory + file_name)
    
    return True

def cd_tray_watcher_dbus():    
    bus = dbus.SystemBus()
    bus.add_signal_receiver(cd_tray_media_changed, 'DeviceChanged', 'org.freedesktop.UDisks', path='/org/freedesktop/UDisks')
    print "Added signal receiver"
    #DriveEject (in'as'options)

def get_udisk_property(device,prop):
    '''
    @param device: a dbus proxy object pointing to org.freedesktop.UDisks
        disk = bus.get_object('org.freedesktop.UDisks','/org/freedesktop/devices/sr0')
    '''
    return device.Get('org.freedesktop.UDisks.Device',prop,dbus_interface='org.freedesktop.DBus.Properties')    

def cd_tray_media_changed(device):
    '''
    @summary: Called by cd_tray_watcher_dbus when the DeviceChanged signal is received 
    @param device: A device object -- http://udisks.freedesktop.org/docs/1.0.5/Device.html 
    '''
    print "CD Tray changed!"
    print device
    if device != '/org/freedesktop/UDisks/devices/sr0':
        print "Not the Optical Drive"
        return
    
    bus = dbus.SystemBus()
    disk = bus.get_object('org.freedesktop.UDisks',device)
    media = {   'timeStamp'     :   None,
                'label'         :   None,
                'type'          :   None,
                'serial'        :   None,
                'by-id'         :   None
            }
    
    media['timeStamp'] = get_udisk_property(disk, 'DeviceMediaDetectionTime')
    print media['timeStamp']
    if media['timeStamp'] == 0:
        #This will be 0 if there is no media on the device
        print "Empty Drive!"
        return False
    
    media['label'] = get_udisk_property(disk, 'IdLabel')
    media['type'] = get_udisk_property(disk, 'DriveMedia')
    media['serial'] = get_udisk_property(disk, 'DriveSerial')
    media['by-id'] = get_udisk_property(disk, 'DeviceFileById')
    
    print media
    if disk_already_checked(media['label']):
        print "Already Checked"
        return
    
    if not check_if_owned(media['label']):
        print "Already Owned"
        return
    
    print "Ripping"
    mkvMoviePath = rip_with_makemkv(media['label'])
    
    if not mkvMoviePath:
        print "Rip failed"
        return
    
    print "Converting"
    moviePath = convert_with_handbrake(mkvMoviePath)
    
    if not moviePath:
        print "Converting failed"
        return
    
    print "Moving"
    getMovieName = os.path.split(moviePath)[-1]
    outputMoviePath = re.sub('_', '.', getMovieName[:-8] + 'Cr0n1c' +getMovieName[-4:])
    shutil.move(moviePath, os.path.join(OUTPUT_MOVIE_LOCATION, outputMoviePath))
    disk_already_checked(media['label'], False)
    print "Done with %s" % getMovieName 


def program_watcher(): 
    dbWrite('Starting watcher')
    cd_tray_watcher_dbus()
    
    loop = gobject.MainLoop()
    loop.run()
    cleanup_bad_jobs()

if __name__ == '__main__':
    
    if pathExist(list_of_bins) and pathExist(list_of_dirs):
        program_watcher()
        
    else:
        dbWrite('failed to find paths.  Please check autoripper_config to make sure things are set correctly.', True)
    
