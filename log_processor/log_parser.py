import re

TIME_PATTERN = r'\b\d{4}-\d\d-\d\d\s\d\d:\d\d:\d\d\.\d{3}\s\w{3}'
SENDER_PATTERN = r'\[.*\]'
DURATION_PATTERN = r'duration:.*statement:'
STATEMENT_PATTERN = r'statement:.*'


class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self):
        res = []
        with open(self.path, 'r') as log_file:
            for line in log_file.readlines():
                if re.search(TIME_PATTERN, line):
                    res.append(line)
                else:
                    res[-1] += line
        # for i, el in enumerate(res):
        #     print(i, el)

        parsed_log = list()
        for line in res:
            time = re.search(TIME_PATTERN, line)[0]
            sender_find = re.search(TIME_PATTERN+r'\s'+SENDER_PATTERN, line)[0]
            sender = re.search(SENDER_PATTERN, sender_find)[0][1:-1]
            dur_find = re.search(DURATION_PATTERN, line)
            if dur_find:
                duration = re.search(r'\s.*\s', dur_find[0])[0][1:-1]
            else:
                duration = None
            line = re.sub(r'\s', ' ', line)
            stmt_find = re.search(STATEMENT_PATTERN, line)
            if stmt_find:
                stmt = re.search(r':\s.*', stmt_find[0])[0][1:-1]
            else:
                stmt = None

            if stmt:
                parsed_log.append({
                    "time": time.strip(),
                    "sender": sender.strip(),
                    "duration": duration.strip() if duration else '0 ms',
                    "statement": re.sub(r'\s+', ' ', stmt.strip()) if stmt else None
                })
        return parsed_log
    #process_stat = ([(p.info['name'], sum(p.info['cpu_times'] if p.info['cpu_times'] else [0])) for p in
        #sorted(psutil.process_iter(['name', 'cpu_times']), key=lambda p: sum(p.info['cpu_times'][:2] if p.info['cpu_times'] else [0]))][-3:])