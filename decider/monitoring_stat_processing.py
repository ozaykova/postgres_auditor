import json


class StatisticTypes:
    def __init__(self, q50=0, q90=0, avg=0, min=0, max=0):
        self.q50 = q50
        self.q90 = q90
        self.avg = avg
        self.min = min
        self.max = max


class StatisticAggregator:
    def __init__(self, data):
        cpu = []
        ram = []
        mem = []
        connections = []
        for item in data:
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