
import datetime
import time
import re
import os
import subprocess
from file_read_backwards import FileReadBackwards

#please update the below to your ifle paths
pattern = "Totals:\s+[0-9]+\.[0-9]+\s([0-9]+).*$"
logfile = r"C:\users\YOURUSER\desktop\xmr-out.log"
devconpath = r"C:\users\YOURUSER\desktop\devcon.exe"
overdrivepath = r"C:\users\YOURUSER\desktop\overdriventool.exe"
overdriveargs = '-p1Stable -p2Stable'
xmrstakpath = r"C:\users\YOURUSER\desktop\Release"
procname = "xmr-stak.exe"
hashthreshold = 3700
timethreshold = 5

def checkapi():
    #utilize webapi to verify my hashrate is correct on the pool as well
    return 0

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
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=timethreshold)
    print("Modifed: {} Threshold: {}".format(lastmtime, cutoff))
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
    #print('Disabling: {}'.format(r))
    time.sleep(3)
    r = subprocess.Popen('{} enable "PCI\VEN_1002&DEV_687F*"'.format(devconpath))
    #print('Enabling: {}'.format(r))
    #sleep for 10 seconds so overdrive doesn't get fucked
    time.sleep(10)

def overdrive(overdrivepath, overdriveargs):
    print('Applying Overdrive configs')
    r = subprocess.Popen('{} {}'.format(overdrivepath, overdriveargs), shell=True)
    #print('Return {}'.format(r))

while True:
    currenthash = tail(logfile, pattern)
    updating = mtime(logfile, timethreshold)
    print('Hashrate: {}\nLog updating: {}'.format(currenthash, updating))
    if int(currenthash) < hashthreshold:
        print('Hashrate of {} is below set threshold of {}! Resetting all miner settings'.format(currenthash, hashthreshold))
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        subprocess.Popen('start cmd /C "{}\{}"'.format(xmrstakpath, procname), shell=True)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)
    if updating == False:
        print('The logfile ({}) hasn\'t been updating for {} minutes. Restart sequence beginning'.format(logfile, timethreshold))
        stopprocess(procname)
        resetdrivers(devconpath)
        overdrive(overdrivepath, overdriveargs)
        os.chdir(xmrstakpath)
        subprocess.Popen('start cmd /C "{}\{}"'.format(xmrstakpath, procname), shell=True)
        print('Waiting 90 seconds to get new average hash rates...')
        time.sleep(90)

    time.sleep(5)
