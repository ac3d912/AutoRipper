
import subprocess

from time import sleep
from glob import glob

from autoripper_config import *

def convert_with_handbrake(inFile): #Not started yet
    pass
    
    
def rip_with_makemkv(movieName): #Done with initial dev
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
    discInfo = subprocess.check_output([ MAKEMKVCON, '-r', 'info', 'disc:%s' % MAKEMKV_DISK_NUM ])
    
    if re.search('"Failed to open disc"', discInfo):
        return False
    
    #TO rip disk and eject once finished
    if not subprocess.call([ MAKEMKVCON, '--minlength=%d' %settings['minLength'], '-r', '--decrypt', '--directio=%s' %settings['discAccess'], 'mkv', 'disc:%s' % MAKEMKV_DISC_NUM, 'all', RIP_LOCATION, ';', 'eject', '-r' ]):
        cleanup_bad_jobs()
        return False
    
    #Currently I am going to assume that the first track is the track we want, I will add better control once I figure out all the options to makemkvcon
    movieLocation = RIP_LOCATION + movieName + '.mkv'
    shutil.move(RIP_LOCATION + 'title00.mkv', movieLocation)
    return movieLocation
    
    
def check_if_owned(movieName): #Need help
    #Need to find out where xbmc is caching the metadata for the movies
    pass
    
    
def cleanup_bad_jobs(): #done with initial dev
    dirsToCheck = [ RIP_LOCATION, CONVERT_LOCATION ] #May want to add other cleanup locations
    
    for directory in dirsToCheck:
        filesToDelete = [ f for f in os.listdir(directory) ]
    
        for files in filesToDelete:
            os.remove(files)
            
    return True
    
    
def cd_tray_watcher(cdTrayInfo): #done with initial dev
    #This method will only work with linux.  Will use win32api for windows version
    #better option would be to use udisks --monitor instead of blocking, need to see if I can get it to return once the drive has a disk in it
    
    media = {   'timeStamp'     :   None,
                'label'         :   None,
                'type'          :   None
            }
    
    if cdTrayInfo is None:
        timeStamp = None
    else:
        timeStamp = cdTrayInfo['timeStamp']
        
    while True:
        tmp = subprocess.check_output([ 'udisks', '--show-info', BLURAY_DEVICE ])
        
        if not re.search('has media:\W+1',tmp): #Checks to see if drive is empty
            sleep(5)    #This way we are not spiking CPU usage
            continue
        
        media['timeStamp'] = re.findall('has media:\W+\d\W(.*?)\n',tmp)[0]
        media['label'] = re.findall('label:\W+(.*?)\n',tmp)[0]
        media['type'] = re.findall('\W\W+media:\W+(.*?)\n',tmp)[0]
        
        if not media['type'] in [ 'optical_bd', 'optical_dvd']:
            sleep(5)    #This way we are not spiking CPU usage
            continue
        
        if timeStamp == media['timeStamp']:
            sleep(5)    #This way we are not spiking CPU usage
            continue
        
        return media
        
    
def program_watcher(): #done with initial dev
    cdTrayInfo = None

    while True:  
        cleanup_bad_job()  
        movieInfo = cd_tray_watcher(cdTrayInfo)
        
        if check_if_owned(movieInfo['label']):
            continue
        
        mkvMoviePath = rip_with_makemkv(movieInfo['label'])
            
        if not mkvMoviePath:
            continue
        
        if movieInfo['type'] == 'optical_bd' :
            moviePath = convert_with_handbrake(movieInfo, mkvMoviePath)
            
            if not moviePath:
                shutil.move(moviePath, OUTPUT_MOVIE_LOCATION)
        
        else:
            shutil.move(mkvMoviePath, OUTPUT_MOVIE_LOCATION)
    

if __name__ == '__main__':
    
    try:
        program_watcher()
    except:
        cleanup_bad_jobs()
    
