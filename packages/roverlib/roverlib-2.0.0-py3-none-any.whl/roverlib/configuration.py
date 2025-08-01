import threading
import time
from loguru import logger
from roverlib.bootinfo import Service, TypeEnum


class ServiceConfiguration:
    def __init__(self):
        self.float_options : dict[str, float] = {}
        self.string_options : dict[str, str] = {}
        self.tunable : dict[str, bool] = {}
        self.lock = threading.RLock()
        self.last_update : int = int(time.time() * 1000)

    # Returns the float value of the configuration option with the given name, returns an error if the option does not exist or does not exist for this type
    # Reading is NOT thread-safe, but we accept the risks because we assume that the user program will read the configuration values repeatedly
    # If you want to read the configuration values concurrently, you should use the GetFloatSafe method
    def GetFloat(self, name : str) -> float:
        logger.debug(self.float_options)
        if name not in self.float_options:
            logger.critical(f"No float configuration option with name {name}")
            raise NameError(f"No float configuration option with name {name}")

        return self.float_options[name]

    def GetFloatSafe(self, name : str) -> float:
        with self.lock:
            return self.GetFloat(name)


    # Returns the string value of the configuration option with the given name, returns an error if the option does not exist or does not exist for this type
    # Reading is NOT thread-safe, but we accept the risks because we assume that the user program will read the configuration values repeatedly
    # If you want to read the configuration values concurrently, you should use the GetStringSafe method    
    def GetString(self, name : str) -> str:
        if name not in self.string_options:
            logger.critical(f"No string configuration option with name {name}")
            raise NameError(f"No string configuration option with name {name}")

        return self.string_options[name]

    def GetStringSafe(self, name : str) -> str:
        with self.lock:
            return self.GetString(name)

    # Set the float value of the configuration option with the given name (thread-safe)    
    def _SetFloat(self, name : str, value : float):
        with self.lock:
            if name in self.tunable:
                if name not in self.float_options:
                    logger.error(f"{name} : {value} Is not of type Float")
                self.float_options[name] = value
                logger.info(f"{name} : {value} Set float configuration option")
            else:
                logger.error(f"{name} : {value} Attempted to set non-tunable float configuration option")

    # Set the string value of the configuration option with the given name (thread-safe)
    def _SetString(self, name : str, value : str):
        with self.lock:
            if name in self.tunable:
                if name not in self.string_options:
                    logger.error(f"{name} : {value} Is not of type String")
                    return None
                self.float_options[name] = value
                logger.info(f"{name} : {value} Set string configuration option")
            else:
                logger.error(f"{name} : {value} Attempted to set non-tunable string configuration option")



def NewServiceConfiguration(service : Service) -> ServiceConfiguration:
    config = ServiceConfiguration()
    for c in service.configuration:

        if c.type == TypeEnum.NUMBER:
            config.float_options[c.name] = c.value
        elif c.type == TypeEnum.STRING:
            config.string_options[c.name] = c.value

        if c.tunable is True:
            config.tunable[c.name] = c.tunable

    return config
