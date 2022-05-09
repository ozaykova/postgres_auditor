from static_state import *
from db_tools.connector import *
from helpers import *


GB = 1024 * 1024 * 1024
MB = 1024 * 1024


class BasicConfigurator:
    def __init__(self, hw_stat, state, default):
        self.hardware_stat = hw_stat
        self.mem_descr = dict()
        self.autovac_descr = dict()
        self.wal_descr = dict()
        self.config = default
        self.system_state = state
        self.default_conf = default

    def configure_mem(self):
        free_ram = self.system_state.RAM - self.hardware_stat.RAM.q90
        if free_ram <  GB / 10:
            self.config['shared_buffers']['val'] = '250'
            self.config['shared_buffers']['unit'] = 'MB'
        elif free_ram > 2 * GB:
            self.config['shared_buffers']['val'] = '2'
            self.config['shared_buffers']['unit'] = 'GB'
        else:
            ram = int(free_ram * GB / 1024)
            self.config['shared_buffers']['val'] = str(ram)
            self.config['shared_buffers']['unit'] = 'MB'
        self.mem_descr['shared_buffers'] = f'Free RAM space {free_ram / GB} GB, shared buffers should be {self.config["shared_buffers"]["val"]} MB'

        self.config['effective_cache_size']['val'] = str(int(0.75 * self.system_state.RAM / MB))
        self.config['effective_cache_size']['unit'] = 'MB'
        self.mem_descr['effective_cache_size'] = f'Effective cache size should be 75% of RAM ({self.config["effective_cache_size"]["val"]}MB)'

        if self.check_sort_operations():
            self.config['work_mem']['unit'] = 'MB'
            if 0.1 * self.system_state.RAM > free_ram:
                self.config['work_mem']['val'] = str(int(0.25 * self.system_state.RAM / MB / self.system_state.max_connections))
                self.mem_descr['work_mem'] = f'Work memory should be {self.config["work_mem"]["val"]}MB due to huge amount of sort operations and enough RAM'
            else:
                self.config['work_mem']['val'] = str(int(0.1 * self.system_state.RAM / MB / self.system_state.max_connections))
                self.mem_descr['work_mem'] = f'Work memory should be {self.config["work_mem"]["val"]}MB due to huge amount of sort operations and less free RAM'

        self.config['maintenance_work_mem']['val'] = str(int(0.05 * self.system_state.RAM / MB))
        self.config['maintenance_work_mem']['unit'] = 'MB'
        self.mem_descr['maintenance_work_mem'] = f'Maintenance work mem should be around 5% of RAM: {self.config["maintenance_work_mem"]["val"]}MB'

    def check_sort_operations(self):
        return False

    def configure_autovacuum(self):
        if 'autovacuum' in self.default_conf and 'on' not in self.default_conf['autovacuum']['val']:
            self.autovac_descr['autovacuum'] = 'Autovacuum should be turn on'
            self.config['autovacuum']['val'] = 'on'

        if self.system_state.DB_SIZE > 500:
            self.config['autovacuum_vacuum_scale_factor']['val'] = 0.15
            # self.config['autovacuum_vacuum_analyze_factor']['val'] = 0.07
            self.autovac_descr['autovacuum_vacuum_scale_factor'] = f'You have big tables, autovacuum_vacuum_scale_factor should be {self.config["autovacuum_vacuum_scale_factor"]["val"]}'
            # self.autovac_descr['autovacuum_vacuum_analyze_factor'] = f'You have big tables, autovacuum_vacuum_analyze_factor should be {self.config["autovacuum_vacuum_analyze_factor"]["val"]}'

    def configure_wal(self):
        if 'fsync' in self.default_conf and 'off' in self.default_conf['fsync']['val']:
            self.config['fsync']['val'] = 'on'
            self.wal_descr['fsync'] = 'fsync should be turn on, “because if the system crashes without fsync occurring, the cluster will likely be corrupted'

        if 'synchronous_commit' in self.default_conf and 'off' in self.default_conf['synchronous_commit']['val']:
            self.wal_descr['synchronous_commit'] = 'synchronous_commit can be turned off only if you sure that you can lose latest data'

        limit = 32
        self.config['wal_buffers']['val'] = str(min(1/64 * self.system_state.RAM / MB, limit))
        self.config['wal_buffers']['unit'] = 'MB'
        self.wal_descr['wal_buffers'] = f'Wal buffers should be {self.config["wal_buffers"]["val"]}MB - it is 1/32 of shared buffers but no more than 32MB'

    def configure(self):
        self.configure_mem()
        self.configure_autovacuum()
        self.configure_wal()


def main():
    db_info = TargetDbExplorer('demo')
    db_info.init_configuration()
    print(db_info.config)
    print(db_info.get_db_size())

    system_state = StaticState()
    conn = MonitoringDBConnector()
    data = conn.select_monitoring(0)
    hardware_stat = StatisticAggregator(data)
    basic_conf = BasicConfigurator(hardware_stat, system_state, db_info.config)
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