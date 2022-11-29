import json
import os
import threading
from decimal import Decimal
from flask import Flask, request
import psutil
from time import time

sem = threading.Semaphore()

process = psutil.Process(os.getpid())


# http://en.wikipedia.org/wiki/Leibniz_formula_for_%CF%80
def calcPi(n):
    pi, numer = Decimal(0), Decimal(4)
    for i in range(n):
        denom = (2 * i + 1)
        term = numer / denom
        if i % 2:
            pi -= term
        else:
            pi += term
    return pi


app = Flask(__name__)

# endpoint calling calcPi() and
# responding to sender
# http://en.wikipedia.org/wiki/Leibniz_formula_for_%CF%80
@app.route("/calc")
def calculatePI():
    sem.acquire()
    data = json.loads(request.json)
    ApplicationReceived = time()
    calcPi(10000000)
    data['success'] = True
    data['ApplicationReceived'] = ApplicationReceived
    data['ApplicationResponse'] = time()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    sem.release()
    return response

# endpoint responding with the current utilization
@app.route("/getUtilization")
def getWeight():
    cpu = process.cpu_percent()
    mem = process.memory_percent()
    return json.dumps({'utilization': ((cpu + mem) / 2) / 100}),\
           200, {'ContentType': 'application/json'}


# Main Execution
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=False)
