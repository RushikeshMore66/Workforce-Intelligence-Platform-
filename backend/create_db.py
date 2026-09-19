import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='9067717776', dbname='postgres')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname='workforce_intelligence'")
exists = cur.fetchone()
if not exists:
    cur.execute('CREATE DATABASE workforce_intelligence')
    print('Database created: workforce_intelligence')
else:
    print('Database already exists: workforce_intelligence')
conn.close()
print('Done.')
