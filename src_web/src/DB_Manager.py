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

    def execute(self, sql_script):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(sql_script)
        conn.commit()
        conn.close()

    def _prepare_value(self, value):
        if isinstance(value, (list, dict, tuple, set)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def _prepare_rows(self, data):
        print(f"Preparing rows for data: {data[:5]}...") 
        if data is None:
            return []
        if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)):
            return [tuple(self._prepare_value(value) for value in row) for row in data]
        return [tuple(self._prepare_value(v) for v in data)]

    def _ensure_columns(self, conn, table_name, header):
        c = conn.cursor()
        c.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {row[1] for row in c.fetchall()}
        for col in header:
            if col not in existing_cols:
                c.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" TEXT')
        conn.commit()
        
    def insert_data(self, header=[], data=None, table_name="music", type_of_struct='row'):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        header_list = list(header)
        print(f"modified: {data}")
        try :
            if type_of_struct == 'column' and isinstance(data[0], (list, tuple)) :
                data = [[data[i][r] for i in range(len(header_list))]  for r in range(len(data[0]))]
        except Exception as e:
            modified_data = []
            first = True
            for i in data :
                if first :
                    mapped = len(i)
                if len(i)<mapped :
                    i = i + [None]*(mapped-len(i))
                    modified_data.append(i)
                elif len(i)>mapped :
                    i = i[:mapped]
                    modified_data.append(i)
                else :
                    modified_data.append(i)
                first = False
            data = [[modified_data[i][r] for i in range(len(header_list))]  for r in range(len(modified_data[0]))]

        rows = self._prepare_rows(data)
        self._ensure_columns(conn, table_name, header_list)
        placeholders = ', '.join(['?' for _ in header_list])
        cols = ', '.join(f'"{h}"' for h in header_list)
        print(f'Inserting into {table_name} ({cols}) with {len(rows)} rows.')
        c.executemany(f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})', rows)
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

    def write_db(self, header, data, table_name="music", delete_on = None, create=False, type_of_struct='row'):
        print(f"Writing data to {table_name} with header {header} and delete_on {delete_on}...")
        if create : self.create_table(table_name=table_name)
        if delete_on:
            self.modifify_data(type='delete', table_name=table_name
                             , on=delete_on
                             , data=data
                             , header=header
                             , type_of_struct=type_of_struct)
        print('insert_data called with header:', header)
        self.insert_data(header=header, data=data, table_name=table_name, type_of_struct=type_of_struct)

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
    
    def modifify_data(self, type, table_name, on, data, header, update_values=None, type_of_struct='row'):
        print(f"Modifying data in {table_name} with type {type} on columns {on}...")
        if isinstance(on, str):
            on = [on]
        nb = 0
        first = True
        condition = ""
        condition_params = []
        for i, h in enumerate(header):
            if h in on:
                if not first:
                    condition += " OR "
                if type_of_struct == 'column':
                    print(f"Data sample for column {i},{h}: {data[i]}")
                    unique_values = data[i]
                if type_of_struct == 'row':
                    unique_values = list(set(row[i] for row in data))
                    first = False
                if unique_values not in condition_params:
                    if isinstance(unique_values,list):
                        condition_params.extend(unique_values)
                    else:
                        condition_params.append(unique_values)
                placeholders = ', '.join(['?' for _ in condition_params])
                condition += f"{h} IN ({placeholders})"
                nb += 1
            if nb >= len(on):
                break
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if type == 'delete':
            sql = f"DELETE FROM {table_name} WHERE {condition}"
            print(f"Executing SQL: {sql} with params {condition_params}")
            c.execute(sql, condition_params)
        elif type == 'update':
            set_clause = ', '.join([f"{k} = ?" for k in update_values.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            params = list(update_values.values()) + condition_params
            c.execute(sql, params)
        conn.commit()
        conn.close()