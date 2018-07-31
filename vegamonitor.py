import datetime
from file_read_backwards import FileReadBackwards
import json
import os
import re
import requests
import subprocess
import time
import yaml
import sys

with open("config.yaml", 'r') as configfile:
    cfg = yaml.load(configfile)

#load the global variables
devconpath = cfg['global']['devconpath']
overdrivepath = cfg['global']['overdrivepath']
overdriveargs = cfg['global']['overdriveargs']
timethreshold = cfg['global']['timethreshold']
hashthreshold = cfg['global']['hashthreshold']
logsamples = cfg['global']['logsamples']
rejectedshares = cfg['global']['rejectedshares']
pattern = "Totals:\s+[0-9]+\.[0-9]+\s([0-9]+).*$"

applyoverdrive = cfg['actions']['applyoverdrive']
restartdivers = cfg['actions']['restartdivers']

restartreason = ""
devMode = False

metrics = {'hashrate': [], 'onlinetime': [], 'gpuhashes': []}

if 'test' in cfg['global']['context']:
    print "!!! RUNNING IN DEVELOPMENT MODE !!!"
    devMode = True

if restartdivers:
    print "Configured to reset drivers on restart.\n"

if applyoverdrive:
    print "Configured to apply overdrive settings on restart.\n"

if 'XMR' in cfg['global']['app']:
    app = 'XMR'
    path = cfg['xmr-stak']['path']
    procname = cfg['xmr-stak']['procname']
    logfile = cfg['xmr-stak']['logfile']

if 'CAST' in cfg['global']['app']:
    app = 'CAST'
    path = cfg['castxmr']['path']
    procname=  cfg['castxmr']['procname']
    scriptname = cfg['castxmr']['scriptname']
    url = cfg['castxmr']['url']

class bcolors:
    if devMode:
        HEADER = ''
        OKBLUE = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
    else:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def warmupReached(arr):
    return len(arr) >= logsamples

def movingAverage(arr):
    return sum(arr)/len(arr)

def log(arr, sample):
    arr.append(sample)

    if len(arr) > logsamples:
        #pop the oldest reading off the beginning of the list
        arr.pop(0)

def tail(filename, pattern, maxlines=60):
    global restartreason
    waitcount = 0
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

        print(bcolors.WARNING + "No 60s hash found yet. Waiting for that to appear.. ({})".format(waitcount) + bcolors.ENDC)
        waitcount += 1
        if waitcount > 31:
            print(bcolors.FAIL + "Waited too long for an average hash! Kill it all." + bcolors.ENDC)
            restartreason += "{} - Timeout waiting for 60s Hash".format(now)
            restartMiner()
            waitcount = 0
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

def stopProcess(procname):
    r = os.system('taskkill /f /im {}'.format(procname))
    print('Killing {} returned {}'.format(procname, r))

def resetDrivers(devconpath):
    #reset the drivers using devcon. Note this currently is using the CWD of the script, so it needs to be in the same location as this python script
    print('Resetting Drivers')
    r = subprocess.Popen('{} restart "PCI\VEN_1002&DEV_687F*"'.format(devconpath))
    #Starting xmr-stak too fast afterwards was throwing me a gpu error on occasion
    time.sleep(10)

def overdrive(overdrivepath, overdriveargs):
    print('Applying Overdrive configs')
    r = subprocess.Popen('{} {}'.format(overdrivepath, overdriveargs), shell=True)

def startMining(path, procname):
    if "XMR" in app:
        print('Spinning up XMR-stak\n')
        subprocess.Popen('start cmd /C "{}\{}"'.format(path, procname), shell=True)

    if "CAST" in app:
        print('Spinning up Cast-XMR\n')
        subprocess.Popen('start cmd /C "{}\{}"'.format(path, scriptname), shell=True)

def restartMiner():
    #clear the metrics
    global metrics
    metrics = {'hashrate': [], 'onlinetime': [], 'gpuhashes': []}

    if devMode:
        pass

    else:
        stopProcess(procname)
        time.sleep(4)
        try:
            os.remove(logfile)

        except (OSError, NameError) as e:
            pass

        if restartdivers:
            resetDrivers(devconpath)

        if applyoverdrive:
            overdrive(overdrivepath, overdriveargs)

        os.chdir(path)
        startMining(path, procname)

def checkEqual(lst):
   return lst[1:] == lst[:-1]

def XMRStakCheck():
    global restartreason
    if os.path.exists(logfile):
        currenthash = tail(logfile, pattern)
        log(metrics['hashrate'], currenthash)

        updating = mtime(logfile, timethreshold)

        if not warmupReached(metrics['hashrate']):
            #moving average is not accurate yet, so return.
            CURSOR_UP_ONE = '\x1b[1A'
            ERASE_LINE = '\x1b[2K'
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.write(ERASE_LINE)
            msg = "["+str(len(metrics['hashrate']))+"/"+str(logsamples)+"] "
            msg += ('SMA is not ready yet. Waiting')
            for x in range(len(metrics['hashrate'])):
                msg+=('.')
            print msg
            return

        else:
            if movingAverage(metrics['hashrate']) < hashthreshold:
                print(bcolors.FAIL + 'Hashrate of {}H/s is below set threshold of {}! Resetting all miner settings'.format(movingAverage(metrics['hashrate']), hashthreshold) + bcolors.ENDC)
                restartreason += "\n{} - Low Hashrate ({} H/s)".format(now, movingAverage(metrics['hashrate']))
                restartMiner()

            if updating == False:
                print(bcolors.FAIL + 'The logfile ({}) hasn\'t been updating for {} minutes. Restart sequence beginning'.format(logfile, timethreshold) + bcolors.ENDC)
                restartreason += "\n{} - Logfile timeout".format(now)
                restartMiner()

    print(bcolors.OKGREEN + 'Hashrate: {}H/s\nLog updating: {}\n'.format(currenthash, updating) + bcolors.ENDC)

def crashedGPU():
    for x in range(len(metrics['gpuhashes'])):
        if checkEqual(metrics['gpuhashes'][x]):
            return x
    return None

def castXMRCheck():
    global restartreason

    try:
        response = requests.get(url)

    except:
        print(bcolors.FAIL + 'Local webserver threw exception.' + bcolors.ENDC)
        restartMiner()
        restartreason += "\n{} - Webserver caught exception".format(now)
        return

    if response.status_code > 300:
        print(bcolors.FAIL + 'Local webserver returned {}. Is CastXMR down? Restarting just in case.'.format(response.status_code) + bcolors.ENDC)
        restartMiner()
        restartreason += "{} - Web return {}".format(now, response.status_code)

    else:
        loaded = json.loads(response.text)
        currenthash = loaded['total_hash_rate'] / 1000
        numGPU = len(loaded["devices"])

        while len(metrics['gpuhashes']) < numGPU:
            metrics['gpuhashes'].append([])

        #tracker for 'online' minutes
        online = loaded['pool']['online']

        #tracker for rejected shares
        rejected = loaded['shares']['num_rejected']
        rejected += loaded['shares']['num_invalid']

        #use new SMA method
        log(metrics['hashrate'], currenthash)
        log(metrics['onlinetime'], online)
        for x in range(numGPU):
            log(metrics['gpuhashes'][x], loaded["devices"][x]['hash_rate'])

        if devMode:
            print 'hashrate moving average:', movingAverage(metrics['hashrate'])
            print 'hashrate array:', metrics['hashrate']
            print 'online array:', metrics['onlinetime']
            print 'gpuhashes array:', metrics['gpuhashes']

        if not warmupReached(metrics['hashrate']):
            #moving average is not accurate yet, so return.
            CURSOR_UP_ONE = '\x1b[1A'
            ERASE_LINE = '\x1b[2K'
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.write(ERASE_LINE)
            msg = "["+str(len(metrics['hashrate']))+"/"+str(logsamples)+"] "
            msg += ('SMA is not ready yet. Waiting')
            for x in range(len(metrics['hashrate'])):
                msg+=('.')
            print msg
            return

        else:
            if movingAverage(metrics['hashrate']) < hashthreshold:
                print(bcolors.FAIL + 'SMA Hashrate is below set threshold! Resetting all miner settings' + bcolors.ENDC)
                restartreason += "\n{} - Low Hashrate ({} H/s)".format(now, movingAverage(metrics['hashrate']))
                restartMiner()

            elif checkEqual(metrics['hashrate']):
                print(bcolors.FAIL + 'Hashrate is the same across all samples! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
                restartreason += "\n{} - Identical hashrate -- likely CastXMR hang".format(now)
                restartMiner()

            elif crashedGPU() is not None:
                print(bcolors.FAIL + 'GPU{} has crashed! Resetting all miner settings'.format(crashedGPU()) + bcolors.ENDC)
                restartreason += "\n{} - GPU{} crash".format(now, crashedGPU())
                restartMiner()

            elif checkEqual(metrics['onlinetime']):
                print(bcolors.FAIL + 'Online time has been 0 for the past minute! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
                restartreason += "\n{} - Online time of zero -- likely CastXMR hang".format(now)
                restartMiner()

            elif rejected > rejectedshares:
                print(bcolors.FAIL + 'Rejected shares threshold reached! Resetting all miner settings'.format(currenthash, hashthreshold) + bcolors.ENDC)
                restartreason += "\n{} - Too many rejected shares".format(now)
                restartMiner()

        print(bcolors.OKGREEN + 'Hashrate: {}H/s\nWeb request returns: {}\n'.format(currenthash, response.status_code) + bcolors.ENDC)

if __name__ == '__main__':
    while True:
        if warmupReached(metrics['hashrate']):
            print(bcolors.BOLD + '\n\n==============\n' + bcolors.ENDC)

        now = datetime.datetime.now()

        if "XMR" in app:
            XMRStakCheck()

        if "CAST" in app:
            castXMRCheck()

        if restartreason and warmupReached(metrics['hashrate']):
            print(bcolors.BOLD + '======Reasons for Restarts======' + bcolors.ENDC)
            print(bcolors.WARNING + '{}\n'.format(restartreason) + bcolors.ENDC)

        if devMode:
            #might as well speed this up
            time.sleep(timethreshold/5)

        else:
            time.sleep(timethreshold)
