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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tail(filename, pattern, maxlines=20):
    with FileReadBackwards(filename, encoding="utf-8") as frb:
        lines=0
        for l in frb:
            lines += 1
            if lines == maxlines:
                print("I was unable to detect the Totals string in the block i looked at")
                return 0
            if 'Totals' in l:
                hashrate = re.search(pattern, l)
                return hashrate.group(1)

#Gets modified time of the logfile. Confirms it is still updating.
def mtime(logfile, timethreshold):
    lastmtime = datetime.datetime.fromtimestamp(os.path.getmtime(logfile))
    testmtime =  datetime.datetime.fromtimestamp(os.stat(logfile).st_mtime)
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=timethreshold)
    diff = (lastmtime - cutoff) / datetime.timedelta(minutes=1)
    print("Logfile last modified {} minutes ago".format(diff))
    if diff < 3:
        print(bcolors.WARNING + "Last modified time was {} minutes ago. Potential restart incoming".format(diff) + bcolors.ENDC)
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
    r = subprocess.Popen('{} disable "PCI\VEN_1002&DEV_687F*"'.format(devconpath))
    time.sleep(3)
    r = subprocess.Popen('{} enable "PCI\VEN_1002&DEV_687F*"'.format(devconpath))
    #sleep for 10 seconds so overdrive doesn't get fucked
    time.sleep(10)

def overdrive(overdrivepath, overdriveargs):
    print('Applying Overdrive configs')
    r = subprocess.Popen('{} {}'.format(overdrivepath, overdriveargs), shell=True)

while True:
    currenthash = tail(logfile, pattern)
    updating = mtime(logfile, timethreshold)
    if int(currenthash) < hashthreshold:
        print(bcolors.FAIL + 'Hashrate of {} is below set threshold of {}! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        subprocess.Popen('start cmd /C "{}\{}"'.format(xmrstakpath, procname), shell=True)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)
    if updating == False:
        print(bcolors.FAIL + 'The logfile ({}) hasn\'t been updating for {} minutes. Restart sequence beginning'.format(logfile, timethreshold) + bcolors.ENDC)
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        subprocess.Popen('start cmd /C "{}\{}"'.format(xmrstakpath, procname), shell=True)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)
    print(bcolors.BOLD + '\n\n==============\n' + bcolors.ENDC)
    print(bcolors.OKGREEN + 'Hashrate: {}\nLog updating: {}'.format(currenthash, updating) + bcolors.ENDC)
    time.sleep(10)
