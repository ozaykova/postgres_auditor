from log_processor.log_parser import *
from db_tools.connector import *
import os

class LogCollector:
    def __init__(self, directory):
        self.directory = directory
        self.queries = []
        self.total_cnt = 0
        self.sort_cnt = 0
        self.top_requests = set()
        self.conn = TargetDbConnector(CONFIG['db_name'])

    def process(self):
        for filename in os.listdir(self.directory):
            parsed = Parser(os.path.join(self.directory, filename)).parse()
            self.total_cnt += len(parsed)
            self.queries += parsed

            for item in parsed:
                if 'ORDER BY' in item['statement'] or 'order by' in item['statement']:
                    self.sort_cnt += 1

        self.queries.sort(key= lambda x: float(x['duration'][:-3]), reverse=True)

    def fill_top_requests(self, print_it=False):
        self.top_requests.clear()
        for query in self.queries:
            self.top_requests.add(query['statement'])
            if print_it:
                print(str(query['duration']) + ': ' + query['statement'])
            if len(self.top_requests) > 15:
                break

    def explain_queries(self):
        for query in self.top_requests:
            try:
                print(self.conn.get_explanation(query))
            except Exception as e:
                print(e)