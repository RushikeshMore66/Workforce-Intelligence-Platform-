import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='9067717776', dbname='workforce_intelligence')
cur = conn.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)
print('Count:', len(tables))
conn.close()
