from db_tools.connector import *

POSTGRE_SELECT_KEYWORDS = [
    'SELECT',
    'ORDER BY',
    'GROUP BY',
    'WHERE',
    'FROM',
    'HAVING',
    'LIKE',
    'LIMIT',
    'JOIN',
    'ON',
    'USING'
]

class QueryAnalyzer:
    def __init__(self, query):
        self.query = query
        self.parsed_query = []
        self.explained_query = []
        self.recommendations = []
        self.conn = TargetDbConnector(CONFIG['db_name'])

    def explain_queries(self):
        try:
            self.explained_query = self.conn.get_explanation(self.query)
            for i in range (len(self.explained_query)):
                self.explained_query[i] = self.explained_query[i][0]
            # print(self.explained_query)
        except:
            pass

    def parse_query(self):
        tmp = self.query.split(' ')
        tmp_parsed = []
        for i in range(len(tmp)):
            if tmp[i].upper() == 'GROUP' or tmp[i].upper() == 'ORDER' and tmp[i + 1].upper() == 'BY':
                tmp_parsed.append(tmp[i] + ' ' + tmp[i + 1])
                i += 1
            else:
                tmp_parsed.append(tmp[i])

        is_statement_start = True
        for i in range(len(tmp_parsed)):
            if tmp_parsed[i] in POSTGRE_SELECT_KEYWORDS:
                self.parsed_query.append(tmp_parsed[i])
                is_statement_start = True
            else:
                if is_statement_start:
                    self.parsed_query.append(tmp_parsed[i])
                else:
                    self.parsed_query[len(self.parsed_query) - 1] += ' ' + tmp_parsed[i]
                is_statement_start = False

    def search_indexes(self):
        for i in range(len(self.explained_query)):
            if 'Seq Scan on' in self.explained_query[i] and (i < len(self.explained_query) - 1) and 'Filter:' in self.explained_query[i + 1]:
                table = self.explained_query[i][self.explained_query[i].find('Seq Scan on ') + 12:]
                table = table[:table.find(' ')]
                tmp = self.explained_query[i + 1]
                attribute = ''
                attributes_list = []
                for j in range(len(tmp) - 1):
                    if tmp[j + 1] != '(' and tmp[j] == '(':
                        while j < len(tmp) and tmp[j] != ' ':
                            attribute += tmp[j]
                            j += 1
                        if ')' not in attribute:
                            attribute = attribute[1:]
                            attributes_list.append(attribute)
                            attribute = ''
                if attributes_list:
                    self.recommendations.append(f'Index {str(attributes_list)} for table {table}')


    def process_analyze(self):
        self.explain_queries()
        self.parse_query()
        # print(self.parsed_query)
        if len(self.explained_query) > 0:
            self.search_indexes()
            # print(self.recommendations)