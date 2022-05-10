from log_processor.log_parser import *
import os

class LogCollector:
    def __init__(self, directory):
        self.directory = directory
        self.queries = []
        self.total_cnt = 0
        self.sort_cnt = 0
        self.top_requests = set()

    def process(self):
        for filename in os.listdir(self.directory):
            parsed = Parser(os.path.join(self.directory, filename)).parse()
            self.total_cnt += len(parsed)
            self.queries += parsed

            for item in parsed:
                if 'ORDER BY' in item['statement'] or 'order by' in item['statement']:
                    self.sort_cnt += 1

        self.queries.sort(key= lambda x: x['duration'], reverse=True)

        self.top_requests.clear()
        for query in self.queries:
            self.top_requests.add(query['statement'])
            if len(self.top_requests) > 10:
                break
