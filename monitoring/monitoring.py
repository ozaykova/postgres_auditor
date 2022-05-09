from system_state import *
from db_tools.connector import *
import psutil
import platform
import json
from time import time


class Monitoring:
    def __init__(self):
        self.system_info = SystemState()
        self.mem_proc = []
        self.cpu_proc = []

    def fill_system_info(self):
        self.system_info.CPU = psutil.cpu_percent()
        svmem = psutil.virtual_memory()
        self.system_info.RAM = svmem.used
        self.system_info.SSD = psutil.disk_usage('/').used

    def fill_process_activity(self):
        process_data = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'cpu_times', 'memory_percent']):
            process_data.append({'name': p.info['name'], 'cpu_time': sum(p.info['cpu_times'][:2] if p.info['cpu_times'] else [0]),
                                    'cpu_percent': p.info['cpu_percent'] if p.info['cpu_percent'] else 0,
                                    'memory_percent': p.info['memory_percent'] if p.info['memory_percent'] else 0})
        print(process_data)

        process_data.sort(key = lambda a: a['memory_percent'])
        process_data.reverse()

        # TODO: num to config
        for i in range(5):
            self.mem_proc.append(process_data[i])
        print(process_data)

        process_data.sort(key=lambda a: (a['cpu_percent'], a['cpu_time']))
        process_data.reverse()
        for i in range(5):
            if process_data[i] not in self.mem_proc:
                self.cpu_proc.append(process_data[i])

        print(process_data)


def main():
    monitoring = Monitoring()
    monitoring.fill_system_info()
    data = json.dumps(monitoring.system_info.__dict__)
    print(data)
    conn = MonitoringDBConnector()
    conn.insert_monitoring(int(time()), data)
    monitoring.fill_process_activity()

    for p in monitoring.mem_proc:
        conn.insert_process_stat(int(time()), p)
    for p in monitoring.cpu_proc:
        conn.insert_process_stat(int(time()), p)
main()