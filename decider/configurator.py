from static_state import *
from db_tools.connector import *
from helpers import *


GB = 1024 * 1024 * 1024


class Config:
    def __init__(self):
        # Connections
        self.max_connections = 100
        self.superuser_reserved_connections = 3

        # Memory Settings
        self.shared_buffer = None
        self.work_mem = None
        self.maintenance_work_mem = None
        self.effective_cache_size = None
        self.effective_io_concurrency = None
        self.random_page_cost = None

        # Replication
        self.wal_level = None
        self.max_wal_senders = None
        self.synchronous_commit = None

        # WAL
        self.wal_compression = True

        # Replication
        self.max_worker_processes = None
        self.max_parallel_workers_per_gather = None
        self.max_parallel_maintenance_workers = None
        self.max_parallel_workers = None
        self.parallel_leader_participation = None


class BasicConfigurator:
    def __init__(self, hw_stat, state):
        self.hardware_stat = hw_stat
        self.descr = dict()
        self.config = Config()
        self.system_state = state

    def configure_mem(self):
        free_ram = self.system_state.RAM - self.hardware_stat.RAM.q90
        if free_ram <  GB / 10:
            self.config.shared_buffer = '250MB'
        elif free_ram > 2 * GB:
            self.config.shared_buffer = '2GB'
        else:
            ram = int(free_ram * GB / 1024)
            self.config.shared_buffer = str(ram) + 'MB'
        self.descr['shared_buffer'] = f'Free RAM space {free_ram / GB} GB, shared buffers should be {self.config.shared_buffer}'


    def configure(self):
        self.configure_mem()


def main():
    system_state = StaticState()
    conn = MonitoringDBConnector()
    data = conn.select(0)
    default_conf = ConfigParser().parse()
    print (default_conf)
    hardware_stat = StatisticAggregator(data)
    basic_conf = BasicConfigurator(hardware_stat, system_state)
    basic_conf.configure()
    print(basic_conf.descr)
    print(data)
    print(system_state.CPU)

main()