import sqlite3
import os

conn = sqlite3.connect(r'C:\Users\lenovo\Desktop\HomeLab\HOUSIFY\data\housify.db')
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name")
print("=== TABLES ===")
rows = c.fetchall()
conn.close()

out_dir = r'C:\Users\lenovo\Desktop\HomeLab\HOUSIFY\data\sql\CREATE'
os.makedirs(out_dir, exist_ok=True)

for name, sql in rows:
    print(f"Table: {name}")
    if sql:
        with open(os.path.join(out_dir, f"CREATE_TABLE_{name.upper()}.sql"), 'w', encoding='utf-8') as f:
            f.write(sql.replace(',', ',\n').replace('(', '(\n ').replace(')', '\n)') + ';\n')
        print(f"Written: {name}.sql")
