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
        self.Disk = psutil.disk_usage('/').total
        self.is_ssd = True
        self.OS = OS.LINUX if 'Linux' in platform.platform() else OS.MacOS
        self.DB_SIZE = 0
        self.max_connections = 1
