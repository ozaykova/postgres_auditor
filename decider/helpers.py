import json


class StatisticTypes:
    def __init__(self, q50, q90, avg, min, max):
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

        self.CPU = StatisticTypes(cpu[int(len(cpu) / 2)], cpu[int(9 * len(cpu) / 10)], int(sum(cpu)/len(cpu)),
                                  cpu[0], cpu[len(cpu) - 1])
        self.RAM = StatisticTypes(ram[int(len(ram) / 2)], ram[int(9 * len(ram) / 10)], int(sum(ram) / len(ram)),
                                  ram[0], ram[len(ram) - 1])
        self.MEM = StatisticTypes(mem[int(len(mem) / 2)], mem[int(9 * len(mem) / 10)], int(sum(mem) / len(mem)),
                                  mem[0], mem[len(mem) - 1])
        self.CPU = StatisticTypes(connections[int(len(connections) / 2)], connections[int(9 * len(connections) / 10)],
                                  int(sum(connections) / len(connections)),
                                  connections[0], connections[len(connections) - 1])

class ConfigParser:
    def __init__(self):
        self.path = '/opt/homebrew/var/postgres/postgresql.conf'
        self.config = dict()

    def parse(self):
        with open(self.path) as f:
            for line in f.readlines():
                if '=' in line and line[0] != '#':
                    res = line.split('=')
                    key = res[0][0:len(res[0]) - 2]
                    val = res[1][1:res[1].find('\t', 1)]
                    self.config[key] = val
        return self.config
