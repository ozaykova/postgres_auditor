with open('default_select_only') as f:
    conn = 0
    latency = 0
    tps = 0
    init_conn_time = 0
    for line in f.readlines():
        if 'number of clients' in line:
            conn = line[18:-1]
        if 'latency average = ' in line:
            latency = line[17:-3]
        if 'initial connection time = ' in line:
            init_conn_time = line[25:-3]
        if 'tps = ' in line:
            tps = line[5:-35]
            print('{' + '\'conn\': ' + conn + ', \'latency\': ' + latency + ', \'tps\': ' + tps + ', \'init_conn_time\': ' + init_conn_time + '},')