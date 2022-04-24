import psycopg2
from psycopg2.extras import Json


class DBHelper:
    def wrap(input_str):
        return "\'" + input_str + "\'"

class MonitoringDBConnector:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='postgres_auditor', user='postgres', password='1234', host='localhost')
        self.cursor = self.conn.cursor()
        self.wrapper = DBHelper()

    def __del__(self):
        self.conn.close()

    def wrap_special(self, item):
        return item.replace('.', '\.')

    def insert(self, ts=0, json_data = None):
        self.cursor.execute(f"INSERT INTO monitoring (ts, data) VALUES ({ts}, {Json(json_data)});")
        self.conn.commit()

    def select(self, ts=0):
        self.cursor.execute(f"SELECT * FROM monitoring WHERE ts > {ts};")
        return self.cursor.fetchall()