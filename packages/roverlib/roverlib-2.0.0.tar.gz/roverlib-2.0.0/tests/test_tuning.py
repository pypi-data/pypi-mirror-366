"""
Tests for tuning
"""

import roverlib as rover
import time
import signal
from loguru import logger
import roverlib.rovercom as rovercom
import zmq
from .bootinfo import inject_valid_service

def run(service : rover.Service, configuration : rover.ServiceConfiguration):
    ######################################################
    time.sleep(2)
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:8829")

    assert abs(configuration.GetFloatSafe("speed") - 1.5) < 0.01
    
    tuning = rovercom.TuningState(timestamp=int(time.time() * 1000), dynamic_parameters=[
        rovercom.TuningStateParameter(number=rovercom.TuningStateParameterNumberParameter(key="speed",value=1.1))
        ]
    ).SerializeToString()

    for i in range(5):
        socket.send(tuning)
        time.sleep(0.05)


    assert abs(configuration.GetFloatSafe("speed") - 1.1) < 0.01





def onTerminate(sig : signal):
    logger.info("Terminating")
    return None

def test_validation():
    inject_valid_service()
    rover.Run(run, onTerminate)
