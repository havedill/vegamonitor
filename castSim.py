#import the test libs to simulate the cast server
from flask import Flask
import json
import time
import random
from copy import deepcopy

mode = 'crash' #normal, lowhash, online0, samehash, rejected, crash
hashThreshold = 5850*1000
hashrate = hashThreshold + 200000
numGPU = 3

data = json.loads('''{
    "total_hash_rate": 3718861,
    "total_hash_rate_avg": 3850839,
    "pool": {
        "server": "cryptonight.usa.nicehash.com:3355",
        "status": "connected",
        "online": 589,
        "offline": 0,
        "reconnects": 0,
        "time_connected": "2018-03-25 21:11:17",
        "time_disconnected": "2018-03-25 21:11:17"
    },
    "job": {
        "job_number": 10,
        "difficulty": 200007,
        "running": 26,
        "job_time_avg": 62.44
    },
    "shares": {
        "num_accepted": 18,
        "num_rejected": 0,
        "num_invalid": 0,
        "num_network_fail": 0,
        "num_outdated": 0,
        "search_time_avg": 32.56
    },
    "devices": [
    ]
}''')


start = time.time()

# Setup Flask app and app.config
app = Flask(__name__)

def startGPUs():
    print "starting GPUs"

    for x in range(numGPU):
        #build gpu data
        GPU = {"device": "GPU" + str(x),
        "device_id": str(x),
        "hash_rate": 1905402,
        "hash_rate_avg": 2044244,
        "gpu_temperature": 59,
        "gpu_fan_rpm": 3881}

        data['devices'].append(GPU)

def updateGPUs(crashedGPU = None):
    for x in range(numGPU):
        if x != crashedGPU:
            GPU = data['devices'][x]
            GPU['hash_rate'] = (hashrate + random.randint(-50000, 50000))/numGPU
            GPU['hash_rate_avg'] = (hashrate + random.randint(-5000, 5000))/numGPU

@app.route('/')
def castSim():
    if mode == 'crash':
        updateGPUs(crashedGPU=numGPU-1)
    else:
        updateGPUs()

    if mode == 'normal':
        #normal operation: online increases, hashrate is above minimum
        online = time.time() - start
        data['pool']['online'] = int(online)
        data['total_hash_rate'] = hashrate + random.randint(-50000, 50000)
        data['total_hash_rate_avg'] = hashrate + random.randint(-5000, 5000)

    elif mode == 'lowhash':
        #simulate low hashrate
        online = time.time() - start
        data['pool']['online'] = int(online)
        data['total_hash_rate'] = hashThreshold + random.randint(-50000, 50000)
        data['total_hash_rate_avg'] = hashThreshold + random.randint(-5000, 5000)

    elif mode == 'online0':
        #simulate online time of zero
        data['pool']['online'] = 0
        data['total_hash_rate'] = hashrate + random.randint(-50000, 50000)
        data['total_hash_rate_avg'] = hashrate + random.randint(-5000, 5000)

    elif mode == 'samehash':
        #simulate identical hashrates
        online = time.time() - start
        data['pool']['online'] = int(online)
        data['total_hash_rate'] = hashrate
        data['total_hash_rate_avg'] = hashrate
    
    elif mode == 'rejected':
        #simulate rejected shares
        num_invalid = data['shares']['num_invalid'] + 1
        online = time.time() - start
        data['pool']['online'] = int(online)
        data['total_hash_rate'] = hashrate + random.randint(-50000, 50000)
        data['total_hash_rate_avg'] = hashrate + random.randint(-5000, 5000)

    return json.dumps(data)

startGPUs()
app.run(host='0.0.0.0', port=7777, debug=True)