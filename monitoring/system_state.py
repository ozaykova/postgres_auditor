from enum import Enum


class DBType(Enum):
    OLTP = 1
    WebAPP = 2
    DataWarehouse = 3
    Desktop = 4
    Mixed = 5


class SystemState:
    def __init__(self):
        self.CPU = 0
        self.SSD = 0
        self.HDD = 0
        self.RAM = 0
        self.DBType = DBType.Mixed.value
        self.DBSize = 0
        self.max_index_size = 0
        self.max_table_size = 0
        self.read_transactions_cnt = 0
        self.open_connections_cnt = 0
