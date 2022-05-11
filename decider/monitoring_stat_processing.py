import json


class StatisticTypes:
    def __init__(self, q50=0, q90=0, avg=0, min=0, max=0):
        self.q50 = q50
        self.q90 = q90
        self.avg = avg
        self.min = min
        self.max = max


class StatisticAggregator:
    def __init__(self, monitoring_data, per_process_data):
        cpu = []
        ram = []
        mem = []
        connections = []
        for item in monitoring_data:
            d = json.loads(item[1])
            cpu.append(d['CPU'])
            ram.append(d['RAM'])
            mem.append(d['SSD'])
            connections.append(d['open_connections_cnt'])

        cpu.sort()
        ram.sort()
        mem.sort()
        connections.sort()

        self.CPU = StatisticTypes()
        self.RAM = StatisticTypes()
        self.MEM = StatisticTypes()
        self.Connections = StatisticTypes()
        self.is_high_cpu_load = True
        self.is_high_mem_load = True

        if len(cpu) > 0:
            self.CPU = StatisticTypes(cpu[int(len(cpu) / 2)], cpu[int(9 * len(cpu) / 10)], int(sum(cpu)/len(cpu)),
                                      cpu[0], cpu[len(cpu) - 1])
            self.RAM = StatisticTypes(ram[int(len(ram) / 2)], ram[int(9 * len(ram) / 10)], int(sum(ram) / len(ram)),
                                      ram[0], ram[len(ram) - 1])
            self.MEM = StatisticTypes(mem[int(len(mem) / 2)], mem[int(9 * len(mem) / 10)], int(sum(mem) / len(mem)),
                                      mem[0], mem[len(mem) - 1])
            self.Connections = StatisticTypes(connections[int(len(connections) / 2)], connections[int(9 * len(connections) / 10)],
                                      int(sum(connections) / len(connections)),
                                      connections[0], connections[len(connections) - 1])

        self.per_process_aggregation = dict()
        for item in per_process_data:
            stripped_item = item[1].strip()
            if item[1] not in self.per_process_aggregation:
                self.per_process_aggregation[stripped_item] = dict()
                self.per_process_aggregation[stripped_item]['CPU_Perc'] = item[2]
                self.per_process_aggregation[stripped_item]['CPU'] = item[3]
                self.per_process_aggregation[stripped_item]['MEM'] = item[4]
            else:
                self.per_process_aggregation[stripped_item]['CPU_Perc'] = max(item[2], self.per_process_aggregation[stripped_item]['CPU_Perc'])
                self.per_process_aggregation[stripped_item]['CPU'] += item[3]
                self.per_process_aggregation[stripped_item]['MEM'] = max(item[4], self.per_process_aggregation[stripped_item]['MEM'])


        self.process_by_cpu = sorted(
            [(process, vals['CPU']) for process, vals in self.per_process_aggregation.items()],
            key=lambda x: x[1],
            reverse=True
        )
        self.process_by_mem = sorted(
            [(process, vals['MEM']) for process, vals in self.per_process_aggregation.items()],
            key=lambda x: x[1],
            reverse=True
        )

        self.process_by_cpu = self.process_by_cpu[:10]
        self.process_by_mem = self.process_by_mem[:10]

    def print_proc_stat(self):
        print('TOP-10 CPU usage stat (total used CPU time):')
        for item in self.process_by_cpu:
            print(str(item[0]) + ' use ' + str(item[1]))
        print()
        print('TOP-10 memory usage stat (In %):')
        for item in self.process_by_mem:
            print(str(item[0]) + ' use ' + str(item[1]))