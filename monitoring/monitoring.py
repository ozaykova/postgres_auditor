from system_state import *
from db_tools.connector import *
import psutil
import platform
import json
from time import time

class Monitoring:
    def __init__(self):
        self.system_info = SystemState()

    def fill_system_info(self):
        self.system_info.CPU = psutil.cpu_percent()
        svmem = psutil.virtual_memory()
        self.system_info.RAM = svmem.used
        self.system_info.SSD = psutil.disk_usage('/').used


def main():
    monitoring = Monitoring()
    monitoring.fill_system_info()
    data = json.dumps(monitoring.system_info.__dict__)
    print(data)
    conn = MonitoringDBConnector()
    conn.insert(int(time()), data)

main()