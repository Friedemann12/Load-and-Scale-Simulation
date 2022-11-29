import atexit
import json
import os
import socket
import subprocess
import threading
from operator import attrgetter
from time import time, sleep, strftime
import docker
import psutil
import random
import requests
import yaml
from flask import Flask, request

# Flask App Definition
loadbalancer = Flask(__name__)

# Backend class definition
class Backend:
    def __init__(self, port, weight):
        self.port = port
        self.weight = weight
        self.userCount = 0
        self.usageCount = 0
        self.serviceTime = 1
        self.selectionProbability = 0
        self.utilization = 0
        self.isStopping = False


# Class to save all backend and
# and keeping track of the index of the
# next backend
class BackendList:
    Backends = []
    next = 0


# GLOBALS
stoppingThreads = False
BackendList = BackendList()
ContainerList = []
ContainerBackendDict = {}
client = docker.from_env()
totalRequests = 0
servedRequests = 0

# Configuration Variables
with open("config.yml") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)
    path = config["path"]
    numberOfInstances = config["numberOfInstances"]
    portLoadbalancer = config["portLoadbalancer"]
    imageName = config["imageName"]
    dockerPort = config["dockerPort"]
    loadbalancingAlgorithm = config["loadbalancingAlgorithm"]
    scalingMechanism = config["scalingMechanism"]
    upperUtilizationLimit = config["upperUtilizationLimit"]
    lowerUtilizationLimit = config["lowerUtilizationLimit"]
    maxContainer = config["maxContainer"]
    numberOfClients = config["numberOfClients"]
    filePath = config["filePath"]

# function to get next Backend
# depending on the configured algorithm
def getNextBackend() -> Backend:
    match loadbalancingAlgorithm:
        case "random":
            backend = None
            while backend is None:
                backend = random.choice(BackendList.Backends)
                if backend.isStopping:
                    backend = None
            backend.usageCount += 1
            return backend
        case "RR":
            index = BackendList.next
            backend = BackendList.Backends[index]
            BackendList.next = (index + 1) % len(BackendList.Backends)
            backend.usageCount += 1
            return backend
        case "AWRR":
            updateWeights()
            backend = max(BackendList.Backends, key=attrgetter("selectionProbability"))
            backend.usageCount += 1
            return backend
        case _:
            return BackendList.Backends[0]


# function returning the total
# weight of all Backends
def getTotalWeight():
    totalWeight = 0
    for backend in BackendList.Backends:
        totalWeight += 1 / backend.serviceTime
    return totalWeight

# function returning the utilization of
# all backend via their /getUtilization endpoint
def getUtilization():
    Utilization = 0
    for backend in BackendList.Backends:
        sleep(0.1)
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        response = requests.get("http://localhost:{}".format(backend.port) + "/getUtilization"
                                , headers=headers)
        Utilization += json.loads(response.content)["utilization"]  # backend.utilization
        backend.utilization = min(0.99, Utilization + (backend.userCount / 100) * 2)
    return Utilization / len(BackendList.Backends)

# function updating the weights of all backends
# if scaling on, via their /getUtilization endpoint
def updateWeights():
    totalWeight = getTotalWeight()
    dynamicTotal = 0
    for backend in BackendList.Backends:
        if scalingMechanism == "none":
            sleep(0.1)
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
            }
            response = requests.get("http://localhost:{}".format(backend.port) + "/getUtilization"
                                    , headers=headers)
            Utilization = json.loads(response.content)["utilization"]
            backend.utilization = min(0.99, Utilization + (backend.userCount / 100) * 2)
        backend.weight = (1 / backend.serviceTime) / totalWeight
        dynamicTotal += (backend.weight * (1 - backend.utilization))
    for backend in BackendList.Backends:
        backend.selectionProbability = (backend.weight * 1 - backend.utilization) / dynamicTotal
        # if backend.userCount > 0:
        #    selectionProbability = 0
        # backend.selectionProbability = selectionProbability


# endpoint to terminate Loadbalancer runtime and metrics capturing
@loadbalancer.route("/shutdown", methods=['GET'])
def shutdown():
    signal_handler()
    return "Shutting down..."

# main application endpoint
@loadbalancer.route('/')
def router():
    LoadbalancerReceived = time()
    global totalRequests
    totalRequests += 1
    backend = getNextBackend()
    print(f"Serving from Port: {backend.port}")
    backend.userCount += 1
    data = json.loads(request.json)
    sleep(0.2)
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    response = requests.get("http://localhost:{}".format(backend.port) + path, json=json.dumps(data),
                            headers=headers)
    print(response)
    data = response.json()
    data["LoadbalancerReceived"] = str(LoadbalancerReceived)
    data["LoadbalancerResponse"] = str(time())
    response = loadbalancer.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    global servedRequests
    servedRequests += 1
    backend.userCount -= 1
    return response

# function starting container
def startContainer():
    con = client.containers.run(imageName, detach=True, ports={dockerPort: get_free_port()})
    ContainerList.append(con)
    backend = Backend(list(con.attrs["HostConfig"]["PortBindings"].values())[0][0]["HostPort"], 0)
    BackendList.Backends.append(backend)
    ContainerBackendDict[backend] = con

# function stopping and removing container
def stopAndRemoveContainer(container):
    ContainerList.remove(container)
    backend = list(ContainerBackendDict.keys())[list(ContainerBackendDict.values()).index(container)]
    backend.isStopping = True
    ContainerBackendDict.pop(backend)
    BackendList.Backends.remove(backend)
    print("Backend removed, stopping Container")
    container.remove(force=True)

# function to stop an remove all containers
def stopAndRemoveAllContainer():
    for container in ContainerList:
        container.remove(force=True)

# function returning a free port
def get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

# function to handle outer termination
def signal_handler():
    print("Stopping Observers")
    global stoppingThreads
    stoppingThreads = True
    print("Observers stopped")
    print("Stopping Container")
    stopAndRemoveAllContainer()
    print("All Container stopped")
    dockerStatsCapture.terminate()


# function returning a low utilised or idle backend
def getIdleOrLowUtilisedBackend():
    backend = next(backend for backend in BackendList.Backends if not backend.userCount > 0)
    if backend is None:
        backend = min(BackendList.Backends, key=attrgetter("utilization"))
    if backend.userCount > 0:
        return None
    return backend

# function checking Utilization every 5 seconds
def checkUtilization():
    sleep(5)
    while not stoppingThreads:
        print(f"Pending Requests: {totalRequests - servedRequests}")
        totalUtilization = getUtilization()
        if totalUtilization >= upperUtilizationLimit and len(
                BackendList.Backends) < maxContainer:
            print("starting New Backend")
            startContainer()
        elif totalUtilization < lowerUtilizationLimit and len(BackendList.Backends) > 1:
            backend = getIdleOrLowUtilisedBackend()
            if backend is not None:
                print("Removing Backend")
                stopAndRemoveContainer(ContainerBackendDict[backend])
        else:
            print("Nothing todo")
        sleep(5)

# function capturing LB metrics every second
def captureMetrics():
    filename = f"{filePath}LoadbalancerStats_{strftime('%Y.%m.%d-%H:%M:%S')}" \
               f"_Sn={numberOfInstances}_LA={loadbalancingAlgorithm}_SM={scalingMechanism}.txt"
    f = open(filename, "a")
    f.write("Time:CPU:Memory\n")
    f.close()
    while not stoppingThreads:
        f = open(filename, "a")
        cpu = process.cpu_percent()
        mem = process.memory_info().rss / 1024 ** 2
        f.write(f"{time()}:{cpu} %:{mem} MiB\n")
        f.close()
        sleep(1)


# Main Execution
if __name__ == '__main__':
    process = psutil.Process(os.getpid())
    atexit.register(signal_handler)
    i = 0
    for i in range(numberOfInstances):
        startContainer()
    print(f"{i + 1} Container started")
    if scalingMechanism != "none":
        App_observerThread = threading.Thread(target=checkUtilization, name="App_observer")
        App_observerThread.daemon = True
        App_observerThread.start()
    LB_observerThread = threading.Thread(target=captureMetrics, name="LB_observer")
    LB_observerThread.daemon = True
    LB_observerThread.start()
    dockerStatsCapture = subprocess.Popen(["sh",
                                           "./dockerStatsCapture.sh",
                                           f"{filePath}ContainerStats_"
                                           f"{strftime('%Y.%m.%d-%H:%M:%S')}"
                                           f"_Sn={numberOfInstances}"
                                           f"_LA={loadbalancingAlgorithm}"
                                           f"_SM={scalingMechanism}"])
    loadbalancer.run(host='0.0.0.0', port=portLoadbalancer, threaded=True)
