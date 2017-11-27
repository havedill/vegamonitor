import datetime
import time
import re
import os
import subprocess
from file_read_backwards import FileReadBackwards

#################CONFIG SETTINGS#################
#Todo: split this into a seperate file?
#
#Notes: By default i have all these executables set to always run as administrator!
logfile = r"C:\users\YOURUSER\desktop\xmr-out.log"
devconpath = r"C:\users\YOURUSER\desktop\devcon.exe"
overdrivepath = r"C:\users\YOURUSER\desktop\overdriventool.exe"
# "Stable" would be replaced with your saved config's name in OverDriveNTool
overdriveargs = '-p1Stable -p2Stable'
xmrstakpath = r"C:\users\YOURUSER\desktop\Release"
procname = "xmr-stak.exe"
hashthreshold = 3700
timethreshold = 10

pattern = "Totals:\s+[0-9]+\.[0-9]+\s([0-9]+).*$"
restartreason = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tail(filename, pattern, maxlines=60):
    found = None
    while True:
        with FileReadBackwards(filename, encoding="utf-8") as frb:
            lines=0
            for l in frb:
                lines += 1
                #I dont want to scan old logs. So break this loop if before we go too deep.
                if lines > maxlines:
                    continue
                if 'Totals' in l:
                    hashrate = re.search(pattern, l)
                    if hashrate:
                        return hashrate.group(1)
        print(bcolors.WARNING + "No 60s hash found yet. Waiting for that to appear.." + bcolors.ENDC)
        time.sleep(10)


#Gets modified time of the logfile. Confirms it is still updating.
def mtime(logfile, timethreshold):
    lastmtime = datetime.datetime.fromtimestamp(os.path.getmtime(logfile))
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=timethreshold)
    diff = (lastmtime - cutoff) / datetime.timedelta(minutes=1)
    if diff < (timethreshold / 2):
        print(bcolors.WARNING + "Potential restart incoming. {} minutes until we deem stale".format(diff) + bcolors.ENDC)
    else:
        print("Logfile timeout countdown {} minutes".format(diff))
    if lastmtime > cutoff:
        #The file is updating actively
        return True
    else:
        #File stopped updating.
        return False

def stopprocess(procname):
    r = os.system('taskkill /f /im {}'.format(procname))
    print('Killing {} returned {}'.format(procname, r))

def resetdrivers(devconpath):
    #reset the drivers using devcon. Note this currently is using the CWD of the script, so it needs to be in the same location as this python script
    print('Resetting Drivers')
    r = subprocess.Popen('{} restart "PCI\VEN_1002&DEV_687F*"'.format(devconpath))

def overdrive(overdrivepath, overdriveargs):
    print('Applying Overdrive configs')
    r = subprocess.Popen('{} {}'.format(overdrivepath, overdriveargs), shell=True)

def startmining(xmrstakpath, procname):
    print('Spinning up executable')
    subprocess.Popen('start cmd /C "{}\{}"'.format(xmrstakpath, procname), shell=True)

while True:
    print(bcolors.BOLD + '\n\n==============\n' + bcolors.ENDC)
    now = datetime.datetime.now()
    currenthash = tail(logfile, pattern)
    updating = mtime(logfile, timethreshold)
    if int(currenthash) < hashthreshold:
        print(bcolors.FAIL + 'Hashrate of {} is below set threshold of {}! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        startmining(xmrstakpath, procname)
        restartreason += "\ns{} - Low Hashrate ({} H/s)".format(now, currenthash)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)
    if updating == False:
        print(bcolors.FAIL + 'The logfile ({}) hasn\'t been updating for {} minutes. Restart sequence beginning'.format(logfile, timethreshold) + bcolors.ENDC)
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        startmining(xmrstakpath, procname)
        restartreason += "\n{} - Logfile timeout".format(now)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)
    print(bcolors.OKGREEN + 'Hashrate: {}\nLog updating: {}\n'.format(currenthash, updating) + bcolors.ENDC)
    if restartreason:
        print(bcolors.BOLD + '======Reasons for Restarts======' + bcolors.ENDC)
        print(bcolors.WARNING + '{}\n'.format(restartreason) + bcolors.ENDC)
    time.sleep(10)
