import signal
from typing import Callable
from roverlib.configuration import Service, ServiceConfiguration

MainCallback = Callable[[Service, ServiceConfiguration], None]

TerminationCallback = Callable[[signal.Signals], None]
