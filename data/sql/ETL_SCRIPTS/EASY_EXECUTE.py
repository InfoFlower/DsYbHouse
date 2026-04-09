import sqlite3

db_path = "data/housify.db"
sql_file_path = r"data\sql\ETL_SCRIPTS\CONSOLIDATE.sql"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
    sql_script = sql_file.read()

    results = cursor.execute(sql_script).fetchall()
    # Get column names from cursor description
    headers = [description[0] for description in cursor.description]
    with open('output.csv', 'w', encoding='utf-8') as output_file:
        output_file.write('"'+'","'.join(headers) + '"\n')
        for row in results:
            output_file.write('"'+'","'.join(map(str, row)).replace(f'\n\r','/').replace(f'\r\n','/').replace(f'\n','/').replace(f'\r','/') + '"\n')

conn.commit()