#import the test libs to simulate the cast server
from flask import Flask
import json
import time
import random

mode = 'normal' #normal, lowhash, online0, samehash 
hashThreshold = 3650*1000
hashrate = hashThreshold + 200000

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
        "num_invalid": 1,
        "num_network_fail": 0,
        "num_outdated": 0,
        "search_time_avg": 32.56
    },
    "devices": [
    {
        "device": "GPU0",
        "device_id": 0,
        "hash_rate": 1905402,
        "hash_rate_avg": 2044244,
        "gpu_temperature": 59,
        "gpu_fan_rpm": 3881
    },
    {
        "device": "GPU1",
        "device_id": 1,
        "hash_rate": 1813459,
        "hash_rate_avg": 1806595,
        "gpu_temperature": 60,
        "gpu_fan_rpm": 3412
    }
    ]
}''')

start = time.time()

# Setup Flask app and app.config
app = Flask(__name__)

@app.route('/')
def castSim():
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
        pass

    elif mode == 'samehash':
        #simulate identical hashrates
        online = time.time() - start
        data['pool']['online'] = int(online)
        data['total_hash_rate'] = hashrate
        data['total_hash_rate_avg'] = hashrate
        pass

    return json.dumps(data)

app.run(host='0.0.0.0', port=7777, debug=True)