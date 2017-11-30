import datetime
from file_read_backwards import FileReadBackwards
import json
import os
import re
import requests
import subprocess
import time
import yaml

with open("config.yaml", 'r') as configfile:
    cfg = yaml.load(configfile)

#load the global variables
devconpath = cfg['global']['devconpath']
overdrivepath = cfg['global']['overdrivepath']
overdriveargs = cfg['global']['overdriveargs']
timethreshold = cfg['global']['timethreshold']
hashthreshold = cfg['global']['hashthreshold']
pattern = "Totals:\s+[0-9]+\.[0-9]+\s([0-9]+).*$"
restartreason = ""

if 'XMR' in cfg['global']['app']:
    app = 'XMR'
    path = cfg['xmr-stak']['path']
    procname = cfg['xmr-stak']['procname']
    logfile = cfg['xmr-stak']['logfile']

if 'CAST' in cfg['global']['app']:
    app = 'CAST'
    path = cfg['castxmr']['path']
    procname=  cfg['castxmr']['procname']
    url = cfg['castxmr']['url']

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
    #Starting xmr-stak too fast afterwards was throwing me a gpu error on occasion
    time.sleep(10)

def overdrive(overdrivepath, overdriveargs):
    print('Applying Overdrive configs')
    r = subprocess.Popen('{} {}'.format(overdrivepath, overdriveargs), shell=True)

def startmining(path, procname):
    print('Spinning up executable')
    subprocess.Popen('start cmd /C "{}\{}"'.format(path, procname), shell=True)

def restarttime():
    stopprocess(procname)
    time.sleep(4)
    try:
        os.remove(logfile)
    except OSError:
        pass
    resetdrivers(devconpath)
    overdrive(overdrivepath, overdriveargs)
    os.chdir(path)
    startmining(path, procname)
    print('Waiting 90 seconds to get new average hash rates...')
    time.sleep(90)

def xmrstakcheck():
    if os.path.exists(logfile):
        currenthash = tail(logfile, pattern)
        updating = mtime(logfile, timethreshold)
        if int(currenthash) < hashthreshold:
            print(bcolors.FAIL + 'Hashrate of {} is below set threshold of {}! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
            restarttime
            restartreason += "\ns{} - Low Hashrate ({} H/s)".format(now, currenthash)
        if updating == False:
            print(bcolors.FAIL + 'The logfile ({}) hasn\'t been updating for {} minutes. Restart sequence beginning'.format(logfile, timethreshold) + bcolors.ENDC)
            restarttime
            restartreason += "\n{} - Logfile timeout".format(now)
    print(bcolors.OKGREEN + 'Hashrate: {}\nLog updating: {}\n'.format(currenthash, updating) + bcolors.ENDC)

def castcheck():
    response = requests.get(url)
    print(response)
    json = json.loads(response.text)
    print(json)

while True:
    print(bcolors.BOLD + '\n\n==============\n' + bcolors.ENDC)
    now = datetime.datetime.now()
    if "XMR" in app:
        xmrstakcheck
    if "CAST" in app:
        castcheck
    if restartreason:
        print(bcolors.BOLD + '======Reasons for Restarts======' + bcolors.ENDC)
        print(bcolors.WARNING + '{}\n'.format(restartreason) + bcolors.ENDC)
    time.sleep(10)
