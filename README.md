# postgres_auditor

# Instalation:
Switch this postgres settings: \
log_directory - to logs directory \
logging_collector on \
log_statement all \

Creating database and tables: \
CREATE DATABASE postgres_auditor owner postgres; \
CREATE TABLE monitoring (ts serial not null primary key, data json not null); \
CREATE TABLE processes_activity (ts serial not null, name char(256) not null, cpu_percent real not null, cpu_time real not null, memory_percent real not null, PRIMARY KEY(ts, name));
