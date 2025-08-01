import argparse
import os
import signal
import sys
import threading
import time
import json
from roverlib.bootinfo import Service, service_from_dict
from roverlib.callbacks import MainCallback, TerminationCallback
from roverlib.configuration import ServiceConfiguration, NewServiceConfiguration
from roverlib.streams import write_streams, read_streams

import zmq
from loguru import logger
import roverlib.rovercom as rovercom


def shutdown_streams():
    """
    Properly shutdown all streams and close sockets
    """
    global write_streams, read_streams

    logger.info("Closing all streams...")

    # Close all write stream sockets
    for name, write_stream in write_streams.items():
        if write_stream.stream.socket is not None:
            logger.debug(f"Closing write stream socket: {name}")
            write_stream.stream.socket.close()
            write_stream.stream.socket = None

    # Close all read stream sockets
    for name, read_stream in read_streams.items():
        if read_stream.stream.socket is not None:
            logger.debug(f"Closing read stream socket: {name}")
            read_stream.stream.socket.close()
            read_stream.stream.socket = None

    # Clear the stream dictionaries
    write_streams.clear()
    read_streams.clear()

    logger.info("All streams shut down successfully")


def handle_signals(on_terminate: TerminationCallback):
    def signal_handler(sig, frame):
        logger.warning(f"Signal received: {sig}")

        # Close all streams and sockets properly
        try:
            shutdown_streams()  # This properly closes all sockets and terminates context
        except Exception as e:
            logger.error(f"Error during stream shutdown: {e}")

        # callback to the service
        try:
            on_terminate(sig)
            exit(0)
        except Exception as e:
            logger.info(f"termination error: {e}")
            exit(1)

    # catch SIGTERM or SIGINT
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("Listening for signals...")


# Configures log level and output
def setup_logging(debug: bool, output_path: str, service_name="unknown"):
    logger.remove()
    log_format = (
        "<black>{time: HH:mm}</black> <level>{level}</level> <white>[%s] {file}:{line}</white> <cyan>></cyan> <white>{message}</white>"
        % service_name
    )

    # set level
    logger.add(
        sys.stderr, format=log_format, level="DEBUG" if debug else "INFO", colorize=True
    )

    if output_path:
        logger.add(output_path, format=log_format, level="DEBUG" if debug else "INFO")
        logger.info(f"Logging to file {output_path}")

    logger.info("Logger initialized")


def ota_tuning(service: Service, configuration: ServiceConfiguration):
    context = zmq.Context()
    while True:
        logger.info(
            "Attempting to subscribe to OTA tuning service at %s"
            % service.tuning.address
        )
        # Initialize zmq socket to retrieve OTA tuning values from the service responsible for this

        socket = context.socket(zmq.SUB)

        try:
            socket.connect(service.tuning.address)
            # subscribe to all messages
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
        except zmq.ZMQError as e:
            logger.error(f"Failed to connect/subscribe to OTA tuning service: {e}")
            socket.close()
            time.sleep(5)
            continue

        while True:
            logger.info("Waiting for new tuning values")

            # Receive new configuration, and update this in the shared configuration
            res = socket.recv()

            logger.info("Received new tuning values")

            # convert from over-the-wire format to TuningState struct
            tuning: rovercom.TuningState = rovercom.TuningState().parse(res)

            # Is the timestamp later than the last update?
            if tuning.timestamp <= configuration.last_update:
                logger.info(
                    "Received new tuning values with an outdated timestamp, ignoring..."
                )
                continue

            # Update the configuration (will ignore values that are not tunable)
            for p in tuning.dynamic_parameters:
                if p.number:
                    logger.info(
                        "%s : %s Setting tuning value", p.number.key, p.number.value
                    )
                    configuration._SetFloat(p.number.key, p.number.value)
                elif p.string:
                    logger.info(
                        "%s : %f Setting tuning value", p.string.key, p.string.value
                    )
                    configuration._SetString(p.string.key, p.string.value)
                else:
                    logger.warning("Unknown tuning value type")


def Run(main: MainCallback, on_terminate: TerminationCallback):
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="show all logs (including debug)"
    )
    parser.add_argument(
        "--output", type=str, default="", help="path of the output file to log to"
    )

    args = parser.parse_args()

    debug = args.debug
    output = args.output

    #  Fetch and parse service definition as injected by roverd
    definition = os.getenv("ASE_SERVICE")
    if definition is None:
        raise RuntimeError(
            "No service definition found in environment variable ASE_SERVICE. Are you sure that this service is started by roverd?"
        )

    service_dict = json.loads(definition)
    service = service_from_dict(service_dict)

    # enable logging using loguru
    setup_logging(debug, output, service.name)

    # setup for catching SIGTERM and SIGINT, once setup this will run in the background; no active thread needed
    handle_signals(on_terminate)

    # Create a configuration for this service that will be shared with the user program
    configuration = NewServiceConfiguration(service)

    # Support ota tuning in this thread
    # (the user program can fetch the latest value from the configuration)
    if service.tuning.enabled:
        thread_tuning = threading.Thread(
            target=ota_tuning, args=(service, configuration), daemon=True
        )
        thread_tuning.start()

    # Run the user program
    main(service, configuration)
