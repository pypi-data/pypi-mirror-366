"""
Basic tests
"""

import roverlib as rover
import time
import signal
from loguru import logger
import roverlib.rovercom as rovercom
import threading
from .bootinfo import inject_valid_service

runThread = True

def send_continuous(stream : rover.WriteStream):
    while runThread:
        time.sleep(1)
        stream.Write(
            rovercom.SensorOutput(
                sensor_id=2,
                timestamp=int(time.time() * 1000),
                controller_output=rovercom.ControllerOutput(
                    steering_angle=float(1),
                    left_throttle=float(0),
                    right_throttle=float(0),
                    front_lights=False
                ),
            ) 
        )

def run(service : rover.Service, configuration : rover.ServiceConfiguration):
    time.sleep(1)

    speed = configuration.GetFloatSafe("speed")
    logger.info(speed)
    assert speed == 1.5

    
    ll = configuration.GetStringSafe("log-level")
    logger.info(ll)
    assert ll == "debug"

    maxIt = configuration.GetFloat("max-iterations")
    logger.info(maxIt)
    assert maxIt == 100
    
    ######################################################

    wr : rover.WriteStream = service.GetWriteStream("motor_movement")
    rd : rover.ReadStream = service.GetReadStream("imaging", "track_data")
    
    
    thread_send = threading.Thread(target=send_continuous, args=(wr,), daemon=True)
    thread_send.start()

    output = rd.Read()

    global runThread 
    runThread = False
   
    assert output.sensor_id == 2

    
def onTerminate(sig : signal):
    logger.info("Terminating")
    return None


def test_basic():
    inject_valid_service()
    rover.Run(run, onTerminate)

