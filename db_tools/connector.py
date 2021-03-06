import psycopg2
from psycopg2.extras import Json
from decider.config import CONFIG


class DBHelper:
    def wrap(self, input_str):
        return "\'" + input_str + "\'"

class MonitoringDBConnector:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='postgres_auditor', user=CONFIG['user'], password=CONFIG['password'], host='localhost')
        self.cursor = self.conn.cursor()
        self.wrapper = DBHelper()

    def __del__(self):
        self.conn.close()

    def wrap_special(self, item):
        return item.replace('.', '\.')

    def insert_monitoring(self, ts=0, json_data = None):
        self.cursor.execute(f"INSERT INTO monitoring (ts, data) VALUES ({ts}, {Json(json_data)});")
        self.conn.commit()

    def select_monitoring(self, ts=0):
        self.cursor.execute(f"SELECT * FROM monitoring WHERE ts > {ts};")
        return self.cursor.fetchall()

    def insert_process_stat(self, ts=0, data = {}):
        self.cursor.execute(f"INSERT INTO processes_activity (ts, name, cpu_percent, cpu_time, memory_percent) "
                            f"VALUES ({ts}, {self.wrapper.wrap(data['name'])}, {data['cpu_percent']}, {data['cpu_time']}, {data['memory_percent']});")
        self.conn.commit()

    def select_process_stat(self, ts=0):
        self.cursor.execute(f"SELECT * FROM processes_activity WHERE ts > {ts};")
        return self.cursor.fetchall()

class TargetDbConnector:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = psycopg2.connect(dbname=db_name, user=CONFIG['user'], password=CONFIG['password'], host='localhost')
        self.cursor = self.conn.cursor()
        self.wrapper = DBHelper()

    def __del__(self):
        self.conn.close()

    def select_settings(self):
        self.cursor.execute(f"select name, setting, unit from pg_settings;")
        return self.cursor.fetchall()

    def get_db_size(self):
        self.cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{self.db_name}'));")
        return self.cursor.fetchall()

    def get_connections_count(self):
        self.cursor.execute(f"SELECT sum(numbackends) FROM pg_stat_database;")
        return self.cursor.fetchall()

    def get_indexes_sizes(self):
        self.cursor.execute(f"SELECT relname AS \"relation\", pg_size_pretty (pg_relation_size (C .oid)) AS \"total_size\" " \
            "FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C .relnamespace) WHERE nspname NOT IN ('pg_catalog', 'information_schema') " \
            "AND C .relkind <> 'i' AND nspname !~ '^pg_toast' ORDER BY pg_relation_size (C .oid) DESC LIMIT 1;")
        return self.cursor.fetchall()

    def get_biggest_table_size(self):
        self.cursor.execute(f"SELECT relname AS \"tables\", pg_size_pretty (pg_total_relation_size (X .oid)) AS \"size\" "
                            f"FROM pg_class X LEFT JOIN pg_namespace Y ON (Y.oid = X .relnamespace) WHERE "
                            f"nspname NOT IN ('pg_catalog', 'information_schema') AND X .relkind <> 'i' AND nspname !~ '^pg_toast' "
                            f"ORDER BY pg_total_relation_size (X .oid) DESC LIMIT 1;")
        return self.cursor.fetchall()

    def get_explanation(self, query):
        try:
            self.cursor.execute(f'explain {str(query)}')
        except:
            self.conn.rollback()
        return self.cursor.fetchall()