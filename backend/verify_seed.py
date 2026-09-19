import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='9067717776', dbname='workforce_intelligence')
cur = conn.cursor()
tables = ['users', 'supervisors', 'team_leaders', 'teams', 'workers', 'projects', 'tasks', 'blockers', 'work_updates', 'project_activities', 'notifications', 'task_transitions']
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"  {t}: {count}")
conn.close()
