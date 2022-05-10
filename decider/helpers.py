from db_tools.connector import TargetDbConnector


class ConfigParser:
    def __init__(self):
        self.path = '/opt/homebrew/var/postgres/postgresql.conf'
        self.config = dict()

    def parse(self):
        with open(self.path) as f:
            for line in f.readlines():
                if '=' in line and line[0] != '#':
                    res = line.split('=')
                    key = res[0][0:len(res[0]) - 1]
                    val = res[1][1:res[1].find('\t', 1)]
                    self.config[key] = val
        return self.config


class TargetDbExplorer:
    def __init__(self, name):
        self.config = {}
        self.db_name = name
        self.conn = TargetDbConnector(self.db_name)

    def init_configuration(self):
        settings = self.conn.select_settings()

        for setting in settings:
            self.config[setting[0]] = {'val': setting[1], 'unit': setting[2]}

    def convert_data(self, unit, cur_size):
        actual_size = 0.0
        if unit == 'MB':
            actual_size = float(cur_size[:-3])
        if unit == 'GB':
            actual_size = float(cur_size[:-3]) * 1024
        if unit == 'KB' or unit == 'kB':
            actual_size = float(cur_size[:-3]) / 1024
        if unit == 'es':
            actual_size = float(cur_size[:-6]) / 1024 / 1024
        return actual_size

    def get_db_size(self):
        cur_size = self.conn.get_db_size()[0][0]
        unit = cur_size[-2:]
        return self.convert_data(unit, cur_size)

    def get_max_indexes_size(self):
        sizes = self.conn.get_indexes_sizes()
        return self.convert_data(sizes[0][1][-2:], sizes[0][1])

    def get_biggest_table_size(self):
        sizes = self.conn.get_biggest_table_size()
        return self.convert_data(sizes[0][1][-2:], sizes[0][1])


