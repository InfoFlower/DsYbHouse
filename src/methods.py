import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("YTB_API")
from ytb_api import High_level_API

import sqlite3

BASE_DIR = os.getenv('WD')

def request_videos_from_X(search, type, max_results = 50, max_output_length=None): 
    api = High_level_API(api_key)
    res = api.get_all_videos(search, type=type, max_results=max_results, max_output_length=max_output_length)
    return res

def load_csv(file_path):
    with open(BASE_DIR + file_path, 'r', encoding='utf-8') as f:
        header = [h.strip() for h in f.readline().strip()[1:-1].split('";"')]
        data = [tuple(h.strip() for h in line.strip()[1:-1].split('";"')) for line in f]
    return header, data

class db_manager:
    def __init__(self, db_path = 'data/housify.db'):
        self.db_path = f"{BASE_DIR}/{db_path}"
        
    def insert_data(self, header=[], data=None, table_name="music"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        placeholders = ', '.join(['?' for _ in header])
        c.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
        conn.commit()
        conn.close()
    
    def create_table(self, table_name="music"):
        self.structure_file = f"{BASE_DIR}data/sql/CREATE_TABLE_{table_name.upper()}.sql"
        with open(self.structure_file, 'r') as f:
            create_table_sql = f.read()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
        conn.close()

    def write_db(self, header, data, table_name="music"):
        self.create_table(table_name=table_name)
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