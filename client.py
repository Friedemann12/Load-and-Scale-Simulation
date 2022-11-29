import asyncio
import json
import random
import threading
import uuid
from time import time, sleep, strftime
import aiohttp
import requests
import yaml

# async function sending a request to the loadbalancer and awaiting a response
# after receiving a response the function writes all timestamps and information to
# the metrics output file
async def simulateClient(i):
    loop = asyncio.get_event_loop()
    client = aiohttp.ClientSession(loop=loop)
    clientID = str(uuid.uuid1())
    print(f"Starting Client Simulation. ClientId: {clientID}")
    RequestID = str(uuid.uuid1())
    payload = {"uuid": RequestID,
               "clientSend": str(time())
               }
    async with client.get(url, json=json.dumps(payload), headers={
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }) as response:
        assert response.status == 200

        await response.read()
        data = await response.json()
        await client.close()
        clientReceived = time()
        f = open(MetricsFilePath, "a")
        f.write(f"{i}|{data['clientSend']}|RequestID:{RequestID}|Client:{clientID}"
                f"|Send new Request\n")
        f.write(f"{i}|{data['LoadbalancerReceived']}|RequestID: {RequestID}"
                f"|Loadbalancer|Received new Request\n")
        f.write(
            f"{i}|{data['ApplicationReceived']}|RequestID: {RequestID}"
            f"|Application|Received new Request. Starting Calculation\n")
        f.write(
            f"{i}|{data['ApplicationResponse']}|RequestID: {RequestID}"
            f"|Application|Calculation finished. Sending Response\n")
        f.write(f"{i}|{data['LoadbalancerResponse']}|RequestID: {RequestID}"
                f"|Loadbalancer|Request processed\n")
        f.write(f"{i}|{clientReceived}|{RequestID}|RequestID: Client: {clientID}"
                f"|Received Response. Exiting\n")
        f.close()

# Configuration Variables
with open("config.yml") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)
    numberOfInstances = config["numberOfInstances"]
    portLoadbalancer = config["portLoadbalancer"]
    loadbalancingAlgorithm = config["loadbalancingAlgorithm"]
    scalingMechanism = config["scalingMechanism"]
    numberOfClients = config["numberOfClients"]
    filePath = config["filePath"]
    timeBetweenClientsMSMax = config["timeBetweenClientsMSMax"]
    timeBetweenClientsMSMin = config["timeBetweenClientsMSMin"]

MetricsFilePath = f"{filePath}Timestamps_{strftime('%Y.%m.%d-%H:%M:%S')}" \
                  f"_Sn={numberOfInstances}_LA={loadbalancingAlgorithm}" \
                  f"_SM={scalingMechanism}.txt"
url = f"http://localhost:{portLoadbalancer}"

# starting 1 Thread per Client
threads = []
for i in range(numberOfClients):
    t = threading.Thread(target=asyncio.run, args=(simulateClient(i),))
    t.daemon = True
    threads.append(t)
    t.start()
    sleep(random.randint(timeBetweenClientsMSMin, timeBetweenClientsMSMax) / 1000)


# waiting for all clients to finish
for x in threads:
    x.join()

# wait 5 seconds and send termination request to loadbalancer
sleep(5)
requests.get("http://localhost:{}".format(portLoadbalancer) + "/shutdown", headers={
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
})
