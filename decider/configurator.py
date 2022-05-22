from static_state import *
from db_tools.connector import *
from helpers import *
from monitoring_stat_processing import *
from math import log
from log_processor.log_collector import *
from decider.config import CONFIG
from log_processor.query_analyzer import *
from changes_applier.changes_applier import *
import time
import os

GB = 1024 * 1024 * 1024
MB = 1024 * 1024
SECONDS_IN_DAY = 86400


class BasicConfigurator:
    def __init__(self, hw_stat, state, default, total_req_cnt, sort_cnt):
        self.hardware_stat = hw_stat
        self.mem_descr = dict()
        self.autovac_descr = dict()
        self.wal_descr = dict()
        self.planner_descr = dict()
        self.conn_descr = dict()
        self.config = default
        self.system_state = state
        self.default_conf = default
        self.total_req = total_req_cnt
        self.sort_req_cnt = sort_cnt

    def configure_connections(self):
        self.config['max_connections']['val'] = self.hardware_stat.Connections.max + 10 # some epsilon
        self.conn_descr['max_connections'] = f'Max connections should be {self.config["max_connections"]["val"]} due to ' \
                                             f'server has maximum {self.hardware_stat.Connections.max} connections'

    def configure_mem(self):
        free_ram = self.system_state.RAM - self.hardware_stat.RAM.q90
        if free_ram <  GB / 10:
            self.config['shared_buffers']['val'] = '250'
            self.config['shared_buffers']['unit'] = 'MB'
        elif free_ram > 2 * GB:
            self.config['shared_buffers']['val'] = '2'
            self.config['shared_buffers']['unit'] = 'GB'
        else:
            ram = int(free_ram * GB / 4 / MB)
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

        if int(self.config['work_mem']['val']) > 40 and self.config['work_mem']['unit'] == 'MB':
            self.config['hash_mem_multiplier']['val'] = '2.0'
            self.mem_descr['hash_mem_multiplier'] = f'You should increase hash_mem_multiplier up to 2.0 to prevent memory pressure due to' \
                                                    f' server has more than 40MB work_mem setting'

        self.config['maintenance_work_mem']['val'] = str(int(0.05 * self.system_state.RAM / MB))
        self.config['maintenance_work_mem']['unit'] = 'MB'
        self.mem_descr['maintenance_work_mem'] = f'Maintenance work mem should be around 5% of RAM: {self.config["maintenance_work_mem"]["val"]}MB'

    def check_sort_operations(self):
        return 10 * self.sort_req_cnt > self.total_req

    def configure_autovacuum(self):
        if 'autovacuum' in self.default_conf and 'on' not in self.default_conf['autovacuum']['val']:
            self.autovac_descr['autovacuum'] = 'Autovacuum should be turn on'
            self.config['autovacuum']['val'] = 'on'

        self.config['autovacuum_vacuum_cost_delay']['val'] = '2'
        self.config['autovacuum_vacuum_cost_delay']['unit'] = 'ms'
        self.autovac_descr['autovacuum_vacuum_cost_delay'] = f'autovacuum_vacuum_cost_delay should be 2ms for faster vacuum. Be careful with this parameter if server has old processor model'

        if self.system_state.DB_SIZE < 500:
            self.config['autovacuum_vacuum_scale_factor']['val'] = '0.1'
            self.config['autovacuum_analyze_scale_factor']['val'] = '0.2'
            self.autovac_descr[
                'autovacuum_vacuum_scale_factor'] = f'You have small db, autovacuum_vacuum_scale_factor should be {self.config["autovacuum_vacuum_scale_factor"]["val"]}'
            self.autovac_descr[
                'autovacuum_analyze_scale_factor'] = f'autovacuum_vacuum_analyze_factor should be {self.config["autovacuum_analyze_scale_factor"]["val"]}'
            self.config['autovacuum_max_workers']['val'] = '3'
            self.autovac_descr['autovacuum_max_workers'] = f'autovacuum_max_workers should be 3'
        elif 500 < self.system_state.DB_SIZE < 3000:
            self.config['autovacuum_vacuum_scale_factor']['val'] = '0.15'
            self.config['autovacuum_analyze_scale_factor']['val'] = '0.07'
            self.autovac_descr['autovacuum_vacuum_scale_factor'] = f'You have mid-size db, autovacuum_vacuum_scale_factor should be {self.config["autovacuum_vacuum_scale_factor"]["val"]}'
            self.autovac_descr['autovacuum_analyze_scale_factor'] = f'autovacuum_vacuum_analyze_factor should be {self.config["autovacuum_analyze_scale_factor"]["val"]}'
            self.config['autovacuum_max_workers']['val'] = '6'
            self.autovac_descr['autovacuum_max_workers'] = f'autovacuum_max_workers should be 6'
        else:
            self.config['autovacuum_vacuum_scale_factor']['val'] = '0.01'
            self.config['autovacuum_analyze_scale_factor']['val'] = '0.005'
            self.autovac_descr[
                'autovacuum_vacuum_scale_factor'] = f'You have big db, autovacuum_vacuum_scale_factor should be {self.config["autovacuum_vacuum_scale_factor"]["val"]}'
            self.autovac_descr[
                'autovacuum_analyze_scale_factor'] = f'autovacuum_vacuum_analyze_factor should be {self.config["autovacuum_analyze_scale_factor"]["val"]}'
            self.config['autovacuum_max_workers']['val'] = '12'
            self.autovac_descr['autovacuum_max_workers'] = f'autovacuum_max_workers should be 12'

        self.config['autovacuum_work_mem']['val'] = max(int(self.config['maintenance_work_mem']['val']) / max(int(self.config['autovacuum_max_workers']['val']) - 2, 1), 1)
        self.config['autovacuum_work_mem']['unit'] = self.config['maintenance_work_mem']['unit']
        self.autovac_descr['autovacuum_work_mem'] = f'autovacuum_work_mem should be around of work_mem / autovacuum workers count'

    def configure_wal(self):
        if 'fsync' in self.default_conf and 'off' in self.default_conf['fsync']['val']:
            self.config['fsync']['val'] = 'on'
            self.wal_descr['fsync'] = 'fsync should be turn on, because if the system crashes without fsync occurring, the cluster will likely be corrupted'

        if 'synchronous_commit' in self.default_conf and 'off' in self.default_conf['synchronous_commit']['val']:
            self.wal_descr['synchronous_commit'] = 'synchronous_commit can be turned off only if you sure that you can lose latest data'

        limit = 32
        self.config['wal_buffers']['val'] = str(min(1/64 * self.system_state.RAM / MB, limit))
        self.config['wal_buffers']['unit'] = 'MB'
        self.wal_descr['wal_buffers'] = f'Wal buffers should be {self.config["wal_buffers"]["val"]}MB - it is 1/32 of shared buffers but no more than 32MB'

    def configure_planner_cost(self):
        if self.system_state.is_ssd:
            self.config['seq_page_cost']['val'] = '0.1'
            self.config['random_page_cost']['val'] = '0.1'
            self.planner_descr['seq_page_cost'] = f'seq_page_cost and random_page_cost should be equal 0.1 for SSD disks'
        else:
            self.config['seq_page_cost']['val'] = '0.5'
            self.config['random_page_cost']['val'] = '0.5'
            self.planner_descr['seq_page_cost'] = f'seq_page_cost and random_page_cost should be equal 0.5 for HDD disks'

        if self.hardware_stat.is_high_cpu_load or self.hardware_stat.is_high_mem_load:
            self.config['cpu_tuple_cost']['val'] = '0.01'
            self.config['cpu_index_tuple_cost']['val'] = '0.01'
            self.planner_descr['cpu_tuple_cost'] = f'system has high cpu/memory utilization, cpu_tuple_cost should be 0.01 which can result in better query plans'
            self.config['cpu_operator_cost']['val'] = '0.00025'
            self.planner_descr['cpu_operator_cost'] = f'cpu operator cost should be {self.config["cpu_operator_cost"]["val"]}'
        else:
            self.config['cpu_tuple_cost']['val'] = '0.01'
            self.config['cpu_index_tuple_cost']['val'] = '0.01'
            self.planner_descr['cpu_tuple_cost'] = f'system has not high cpu/memory utilization, cpu_tuple_cost should be 0.01 to save row processing speed'
            self.config['cpu_operator_cost']['val'] = '0.0025'
            self.planner_descr[
                'cpu_operator_cost'] = f'cpu operator cost should be {self.config["cpu_operator_cost"]["val"]}'
        self.planner_descr['cpu_index_tuple_cost'] = f'cpu_index_tuple_cost should be equal cpu_tuple_cost'

        if log(self.system_state.max_index_size / int(self.config['min_parallel_index_scan_size']['val'])) / log(3) + 1 > 8:
            self.config['min_parallel_index_scan_size']['val'] = int(self.config['min_parallel_index_scan_size']['val'] * 2)
            self.planner_descr['min_parallel_index_scan_size'] = f'min_parallel_index_scan_size should be {self.config["min_parallel_index_scan_size"]["val"]}' \
                                                                 f' to decrease workers count'

        if log(self.system_state.max_table_size / int(self.config['min_parallel_table_scan_size']['val'])) / log(3) + 1 > 8:
            self.config['min_parallel_table_scan_size']['val'] = int(self.config['min_parallel_table_scan_size']['val'] * 2)
            self.planner_descr['min_parallel_table_scan_size'] = f'min_parallel_table_scan_size should be {self.config["min_parallel_table_scan_size"]["val"]}' \
                                                                 f' to decrease workers count'


    def configure(self):
        self.configure_connections()
        self.configure_mem()
        self.configure_autovacuum()
        self.configure_wal()
        self.configure_planner_cost()


class ConfigRecommendations:
    def __init__(self, conf):
        self.config = conf
        self.recommendations = dict()

    def process(self):
        if self.config['synchronous_commit']['val'] != 'off':
            self.recommendations['synchronous_commit'] = f'can be turned off if there is no fundamental difference' \
                                                         f' whether the user managed to receive a message about successful saving or not'
            self.recommendations['wal_level'] = f'can be minimal if application reliability requirements are limited to crash recovery(without replica recovery)'

def main():
    db_info = TargetDbExplorer('demo')
    db_info.init_configuration()

    system_state = StaticState()
    system_state.DB_SIZE = db_info.get_db_size()
    system_state.max_index_size = db_info.get_max_indexes_size()
    system_state.max_table_size = db_info.get_biggest_table_size()
    conn = MonitoringDBConnector()

    ts = int(time.time())
    start_time = ts - CONFIG['check_days'] * SECONDS_IN_DAY
    monitoring_data = conn.select_monitoring(start_time)
    per_process_data = conn.select_process_stat(start_time)

    hardware_stat = StatisticAggregator(monitoring_data, per_process_data)

    collector = LogCollector(CONFIG['logs_directory'])
    collector.process()

    basic_conf = BasicConfigurator(hardware_stat, system_state, db_info.config, collector.total_cnt, collector.sort_cnt)
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
    print()
    print('Planner-Cost')
    for k, v in basic_conf.planner_descr.items():
        print(v)
    print()
    print('Connections')
    for k, v in basic_conf.conn_descr.items():
        print(v)
    print()

    conf_file = open("postgres_generated.conf", "w+")
    target_path = ''
    conf_path = str(os.getcwd()) + '/' + 'postgres_generated.conf'
    for k, val in basic_conf.config.items():
        if k == 'config_path':
            target_path = val['val']
        if val['val']:
            conf_file.write(str(k) + ' = ' + str(val['val']))
            if val['unit']:
                conf_file.write(' ' + val['unit'])
            conf_file.write('\n')
    while True:
        print('Select an action: \n [1] Show additional recommendations \n [2] Show processes stat \n [3] Show the longest queries'
              '\n [4] Show activity insights \n [5] Show index recommendations \n [6] Apply changes \n [7] Exit')
        action_type = input()
        if action_type == '1':
            print('Additional Recommendations:')
            recommendations = ConfigRecommendations(basic_conf.config)
            recommendations.process()
            for k, v in recommendations.recommendations.items():
                print(str(k) + " " + str(v))
            print('__________________________________')
            print('Select an action: \n [1] Back to main menu \n [2] Exit app')
            action_type = input()
            if action_type == '1':
                continue
            else:
                return

        if action_type == '2':
            print('Processes stat:')
            hardware_stat.print_proc_stat()
            print('__________________________________')
            print('Select an action: \n [1] Back to main menu \n [2] Exit app')
            action_type = input()
            if action_type == '1':
                continue
            else:
                return

        if action_type == '3':
            print('Top of the longest queries:')
            collector.fill_top_requests(print_it=True)
            print('__________________________________')
            print('Select an action: \n [1] Back to main menu \n [2] Exit app')
            action_type = input()
            if action_type == '1':
                continue
            else:
                return

        if action_type == '4':
            hardware_stat.print_activity_insights()
            print('__________________________________')
            print('Select an action: \n [1] Back to main menu \n [2] Exit app')
            action_type = input()
            if action_type == '1':
                continue
            else:
                return

        if action_type == '5':
            print('Indexes recommendations:')
            collector.fill_top_requests()
            recommendations_set = set()
            for query in collector.top_requests:
                # print(query)
                analyzer = QueryAnalyzer(query)
                analyzer.process_analyze()
                recommendations_set.update(analyzer.recommendations)
            for item in recommendations_set:
                print(item)
            print('__________________________________')
            print('Select an action: \n [1] Back to main menu \n [2] Exit app')
            action_type = input()
            if action_type == '1':
                continue
            else:
                return

        if action_type == '6':
            print('Enter hours to sleep:')
            hrs = int(input())
            applier = ChangesApplier(hrs, target_path, conf_path)
            applier.perform_apply()

        if action_type == '7':
            return

main()