import logging
from DB_Utils import build_condition, try_reorganize_data
import sqlalchemy
import os
import json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
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
    def __init__(self, db_path):
        self.db_path = db_path

    def execute(self, sql_script):
        conn = sqlalchemy.create_engine(self.db_path).connect()
        conn.exec_driver_sql(sql_script)
        conn.commit()
        conn.close()

    def _prepare_value(self, value):
        if isinstance(value, (list, dict, tuple, set)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def _prepare_rows(self, data):
        if data is None:
            return []
        if isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], (list, tuple)):
            return [tuple(self._prepare_value(value) for value in row) for row in data]
        return [tuple(self._prepare_value(v) for v in data)]
        
    def insert_data(self, header=[], data=None, table_name="music", type_of_struct='row'):
        header_list = list(header)
        try :
            if type_of_struct == 'column' and isinstance(data[0], (list, tuple)) :
                data = [[data[i][r] for i in range(len(header_list))]  for r in range(len(data[0]))]
        except Exception as e:
            modified_data = try_reorganize_data(data)
            data = [[modified_data[i][r] for i in range(len(header_list))]  for r in range(len(modified_data[0]))]
        rows = self._prepare_rows(data) # self._ensure_columns(conn, table_name, header_list)
        # rows_dicts = [dict(zip(header, row)) for row in rows]
        placeholders = ', '.join(['%s' for _ in header_list])
        cols = ', '.join(f'"{h}"' for h in header_list)
        conn = sqlalchemy.create_engine(self.db_path).connect()
        for row in rows:
            conn.exec_driver_sql(f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})', row)
        conn.exec_driver_sql("COMMIT;")
        conn.close()
    
    def create_table(self, table_name="music"):
        self.structure_file = f"{BASE_DIR}/data/sql/CREATE/CREATE_TABLE_{table_name.upper()}.sql"
        with open(self.structure_file, 'r') as f:
            create_table_sql = f.read()
        conn = sqlalchemy.create_engine(self.db_path).connect()
        conn.exec_driver_sql(create_table_sql)
        conn.exec_driver_sql("COMMIT;")
        conn.close()

    def write_db(self, header, data, table_name="music", delete_on = None, create=False, type_of_struct='row'):
        if create : self.create_table(table_name=table_name)
        if delete_on:
            self.modifify_data(type='delete', table_name=table_name
                             , on=delete_on
                             , data=data
                             , header=header
                             , type_of_struct=type_of_struct)
        self.insert_data(header=header, data=data, table_name=table_name, type_of_struct=type_of_struct)


    def read_db(self, table_name="music", query=None, condition=None, order_by=None, limit=None):
        conn = sqlalchemy.create_engine(self.db_path).connect()
        if query:
            result = conn.exec_driver_sql(query)
        else:
            sql = f"SELECT * FROM {table_name}"
            if condition:
                sql += f" WHERE {condition}"
            if order_by:
                sql += f" ORDER BY {order_by}"
            if limit is not None:
                sql += f" LIMIT {limit}"
            result = conn.exec_driver_sql(sql)
        rows = result.fetchall()
        header = list(result.keys())
        data = [dict(zip(header, row)) for row in rows]
        conn.close()
        logging.debug(f"Read {len(data)} rows from {table_name} with header {header}")
        return header, data
    
    def modifify_data(self, type, table_name, on, data, header, update_values=None, type_of_struct='row'):
        if isinstance(on, str): on = [on]
        condition, condition_params = build_condition(header, data, on, type_of_struct)
        conn = sqlalchemy.create_engine(self.db_path).connect()
        if type == 'delete':
            sql = f"DELETE FROM {table_name} WHERE {table_name}.{condition}"
            conn.exec_driver_sql(sql, tuple(condition_params))
        elif type == 'update':
            set_clause = ', '.join([f"{k} = ?" for k in update_values.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            params = list(update_values.values()) + condition_params
            conn.exec_driver_sql(sql, tuple(params))
        conn.commit()
        conn.close()

# Déprécié
    # def _ensure_columns(self, conn, table_name, header):
    #     result = conn.execute(f"PRAGMA table_info({table_name})")
    #     existing_cols = {row[1] for row in result.fetchall()}
    #     for col in header:
    #         if col not in existing_cols:
    #             conn.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" TEXT;')
    #     conn.commit()