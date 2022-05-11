# postgres_auditor

# Instalation:
Switch this postgres settings: \
log_directory - to logs directory \
logging_collector on \
log_statement all 

Creating database and tables: \
CREATE DATABASE postgres_auditor owner postgres; \
CREATE TABLE monitoring (ts serial not null primary key, data json not null); \
CREATE TABLE processes_activity (ts serial not null, name char(256) not null, cpu_percent real not null, cpu_time real not null, memory_percent real not null, PRIMARY KEY(ts, name));

Change file config.py in decider directory(fill actual info about db, user etc.) \
Add monitoring.py to cron process (recommendation: run it once in 10 min)

# Results
Console input contain: 
1. Settings recommendations
2. Info about resources-bounded processes 
3. Info about queries with most longer duration 
4. File postgres_generated.conf with target configuration

# Future work
1. Explore activity trands based on statistics
2. Explain longest queries and change planner settings + indexes check

