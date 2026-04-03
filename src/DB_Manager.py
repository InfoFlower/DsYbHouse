import sqlite3
import os
import json
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.getenv('WD')

#Utils
def load_csv(file_path):
    with open(BASE_DIR + file_path, 'r', encoding='utf-8') as f:
        header = [h.strip() for h in f.readline().strip()[1:-1].split('";"')]
        data = [tuple(h.strip() for h in line.strip()[1:-1].split('";"')) for line in f]
    return header, data

#Class
class db_manager:
    def __init__(self, db_path = 'data/housify.db'):
        self.db_path = f"{BASE_DIR}/{db_path}"

    def _prepare_value(self, value):
        if isinstance(value, (list, dict, tuple, set)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def _prepare_rows(self, data):
        if data is None:
            return []
        return [tuple(self._prepare_value(value) for value in row) for row in data]
        
    def insert_data(self, header=[], data=None, table_name="music"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        placeholders = ', '.join(['?' for _ in header])
        rows = self._prepare_rows(data)
        c.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
        conn.commit()
        conn.close()
    
    def create_table(self, table_name="music"):
        self.structure_file = f"{BASE_DIR}/data/sql/CREATE/CREATE_TABLE_{table_name.upper()}.sql"
        with open(self.structure_file, 'r') as f:
            create_table_sql = f.read()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
        conn.close()

    def write_db(self, header, data, table_name="music", delete_on = None):
        self.create_table(table_name=table_name)
        if delete_on:
            self.modifify_data(type='delete', table_name=table_name
                             , on=delete_on
                             , data=data
                             , header=header)
        self.insert_data(header=header, data=data, table_name=table_name)

    def read_db(self, table_name="music", query=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if query:
            c.execute(query)
        else:
            c.execute(f"SELECT * FROM {table_name}")
        data = c.fetchall()
        header = [desc[0] for desc in c.description]
        conn.close()
        return header, data
    
    def modifify_data(self, type, table_name, on, data, header, update_values=None):
        nb = 0
        first = True
        condition = ""
        condition_params = []
        for i, h in enumerate(header):
            if h in on:
                if not first:
                    condition += " OR "
                unique_values = list(set(str(row[i]) for row in data))
                placeholders = ', '.join(['?' for _ in unique_values])
                condition += f"{h} IN ({placeholders})"
                condition_params.extend(unique_values)
                nb += 1
                first = False
            if nb >= len(on):
                break
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if type == 'delete':
            sql = f"DELETE FROM {table_name} WHERE {condition}"
            c.execute(sql, condition_params)
        elif type == 'update':
            set_clause = ', '.join([f"{k} = ?" for k in update_values.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            params = list(update_values.values()) + condition_params
            c.execute(sql, params)
        conn.commit()
        conn.close()