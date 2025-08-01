import os
import json

def inject_valid_service():
    service = {
        "name": "controller",
        "version": "1.0.1",
        "inputs": [
            {
                "service": "imaging",
                "streams": [
                    {"name": "track_data", "address": "tcp://localhost:7882"}, #7890
                    {"name": "debug_info", "address": "tcp://unix:7891"}
                ]
            },
            {
                "service": "navigation",
                "streams": [
                    {"name": "location_data", "address": "tcp://unix:7892"}
                ]
            }
        ],
        "outputs": [
            {"name": "motor_movement", "address": "tcp://*:7882"},
            {"name": "sensor_data", "address": "tcp://unix:7883"}
        ],
        "configuration": [
            {"name": "max-iterations", "type": "number", "tunable": True, "value": 100},
            {"name": "speed", "type": "number", "tunable": True, "value": 1.5},
            {"name": "log-level", "type": "string", "tunable": False, "value": "debug"}
        ],
        "tuning": {
            "enabled": True,
            "address": "tcp://localhost:8829"
        }
    }

    os.environ["ASE_SERVICE"] = json.dumps(service)