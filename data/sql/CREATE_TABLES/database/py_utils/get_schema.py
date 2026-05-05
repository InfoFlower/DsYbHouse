import sqlite3

conn = sqlite3.connect('data/housify.db')
c = conn.cursor()

# All tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in c.fetchall()]

print("=== TABLES ===")
for t in tables:
    print(t)

print()
print("=== COLUMNS ===")
for tname in tables:
    c.execute(f"PRAGMA table_info({tname})")
    cols = c.fetchall()
    print(f"[{tname}]")
    for col in cols:
        # col: (cid, name, type, notnull, dflt_value, pk)
        pk = " PK" if col[5] else ""
        notnull = " NOT NULL" if col[3] else ""
        print(f"  {col[1]} ({col[2]}){pk}{notnull}")
    print()

print("=== FOREIGN KEYS ===")
found_any = False
for tname in tables:
    c.execute(f"PRAGMA foreign_key_list({tname})")
    fks = c.fetchall()
    if fks:
        found_any = True
        for fk in fks:
            print(f"  {tname}.{fk[3]} -> {fk[2]}.{fk[4]}")
if not found_any:
    print("  (none defined)")

conn.close()
