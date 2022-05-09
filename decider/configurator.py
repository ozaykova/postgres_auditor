from static_state import *
from db_tools.connector import *
from helpers import *


GB = 1024 * 1024 * 1024
MB = 1024 * 1024

class Config:
    def __init__(self):
        # Connections
        self.max_connections = 100
        self.superuser_reserved_connections = 3

        # Memory Settings
        self.shared_buffers = None
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
        self.fcync = True
        self.wal_buffers = None

        # Replication
        self.max_worker_processes = None
        self.max_parallel_workers_per_gather = None
        self.max_parallel_maintenance_workers = None
        self.max_parallel_workers = None
        self.parallel_leader_participation = None

        #Autovacuum
        self.autovacuum = None
        self.autovacuum_vacuum_scale_factor = None
        self.autovacuum_vacuum_analyze_factor = None


class BasicConfigurator:
    def __init__(self, hw_stat, state, default):
        self.hardware_stat = hw_stat
        self.mem_descr = dict()
        self.autovac_descr = dict()
        self.wal_descr = dict()
        self.config = Config()
        self.system_state = state
        self.default_conf = default

    def configure_mem(self):
        free_ram = self.system_state.RAM - self.hardware_stat.RAM.q90
        if free_ram <  GB / 10:
            self.config.shared_buffers = '250MB'
        elif free_ram > 2 * GB:
            self.config.shared_buffers = '2GB'
        else:
            ram = int(free_ram * GB / 1024)
            self.config.shared_buffers = str(ram) + 'MB'
        self.mem_descr['shared_buffers'] = f'Free RAM space {free_ram / GB} GB, shared buffers should be {self.config.shared_buffers}'

        self.config.effective_cache_size = str(int(0.75 * self.system_state.RAM / MB)) + 'MB'
        self.mem_descr['effective_cache_size'] = f'Effective cache size should be 75% of RAM ({self.config.effective_cache_size})'

        if self.check_sort_operations():
            if 0.1 * self.system_state.RAM > free_ram:
                self.config.work_mem = str(int(0.25 * self.system_state.RAM / MB / self.system_state.max_connections)) + 'MB'
                self.mem_descr['work_mem'] = f'Work memory should be {self.config.work_mem} due to huge amount of sort operations and enough RAM'
            else:
                self.config.work_mem = str(int(0.1 * self.system_state.RAM / MB / self.system_state.max_connections)) + 'MB'
                self.mem_descr['work_mem'] = f'Work memory should be {self.config.work_mem} due to huge amount of sort operations and less free RAM'

        self.config.maintenance_work_mem = str(int(0.05 * self.system_state.RAM / MB)) + 'MB'
        self.mem_descr['maintenance_work_mem'] = f'Maintenance work mem should be around 5% of RAM: {self.config.maintenance_work_mem}'

    def check_sort_operations(self):
        return False

    def configure_autovacuum(self):
        if 'autovacuum' in self.default_conf and 'on' not in self.default_conf['autovacuum']:
            self.autovac_descr['autovacuum'] = 'Autovacuum should be turn on'
            self.config.autovacuum = True

        if self.system_state.DB_SIZE > 500:
            self.config.autovacuum_vacuum_scale_factor = 0.15
            self.config.autovacuum_vacuum_analyze_factor = 0.07
            self.autovac_descr['autovacuum_vacuum_scale_factor'] = f'You have big tables, autovacuum_vacuum_scale_factor should be {self.config.autovacuum_vacuum_scale_factor}'
            self.autovac_descr['autovacuum_vacuum_analyze_factor'] = f'You have big tables, autovacuum_vacuum_analyze_factor should be {self.config.autovacuum_vacuum_analyze_factor}'

    def configure_wal(self):
        if 'fsync' in self.default_conf and 'off' in self.default_conf['fsync']:
            self.config.fcync = True
            self.wal_descr['fsync'] = 'fsync should be turn on, “because if the system crashes without fsync occurring, the cluster will likely be corrupted'

        if 'synchronous_commit' in self.default_conf and 'off' in self.default_conf['synchronous_commit']:
            self.wal_descr['synchronous_commit'] = 'synchronous_commit can be turned off only if you sure that you can lose latest data'

        limit = 32
        self.config.wal_buffers = str(min(1/64 * self.system_state.RAM / MB, 32)) + 'MB'
        self.wal_descr['wal_buffers'] = f'Wal buffers should be {self.config.wal_buffers} - it is 1/32 of shared buffers but no more than 32MB'

    def configure(self):
        self.configure_mem()
        self.configure_autovacuum()
        self.configure_wal()


def main():
    system_state = StaticState()
    conn = MonitoringDBConnector()
    data = conn.select(0)
    default_conf = ConfigParser().parse()
    hardware_stat = StatisticAggregator(data)
    basic_conf = BasicConfigurator(hardware_stat, system_state, default_conf)
    basic_conf.configure()

    print('SETTINGS ADJUSTMENT')
    print('MEMORY')
    for k, v in basic_conf.mem_descr.items():
        print(v)
    print()
    print('AUTOVACUUM')
    for k, v in basic_conf.autovac_descr.items():
        print(v)
    print()
    print('WAL')
    for k, v in basic_conf.wal_descr.items():
        print(v)
main()