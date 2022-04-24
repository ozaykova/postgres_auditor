import multiprocessing
import psutil
import platform
from enum import Enum


class OS(Enum):
    LINUX = 1
    MacOS = 2


class StaticState:
    def __init__(self):
        self.RAM = psutil.virtual_memory().total
        self.CPU = multiprocessing.cpu_count()
        self.SSD = psutil.disk_usage('/').total
        self.OS = OS.LINUX if 'Linux' in platform.platform() else OS.MacOS
