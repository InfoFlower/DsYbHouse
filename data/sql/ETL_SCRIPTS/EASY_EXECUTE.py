import sqlite3
from tabulate import tabulate

PATH = "C:/Users/lenovo/Desktop/HomeLab/HOUSIFY/data/housify.db"


def format_query_result(data, header):
    """Format SQLite query results as a fancy ASCII table."""
    if not data:
        return "No data to display"
    return tabulate(data, headers=header, tablefmt="grid", stralign="center")

with open('C:/Users/lenovo/Desktop/HomeLab/HOUSIFY/data/sql/ETL_SCRIPTS/CONSOLIDATE.sql', 'r') as f:
    sql_script = f.read()
conn = sqlite3.connect(PATH)
c = conn.cursor()  
c.execute(sql_script)
data =c.fetchall()
conn.commit()

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(format_query_result(data, [desc[0] for desc in c.description]))