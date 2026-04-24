import sys
    
sys.path.append('src_web/src')
from DB_Manager import db_manager

class DB_JsonHandler:
    def __init__(self, db_path = 'data/housify.db'):
        self.db_path = db_path
        self.conn = db_manager(db_path)
    
    def create_table(self, json_tables):
        for table_name in json_tables:
            sql_script = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            for table_columns in json_tables[table_name].keys():
                sql_script += f'"{table_columns}" TEXT, '
            sql_script = sql_script[:-2] + ");"
            self.conn.execute(sql_script)

    def insert_data(self, json_tables, key=None):
        for table_name in json_tables:
            print(f"Inserting data into {table_name}...")
            data = [json_tables[table_name][column] for column in json_tables[table_name].keys()]
            
            self.conn.write_db(header=json_tables[table_name].keys(), 
                               data=data, 
                               table_name=table_name,
                               delete_on=key,
                               type_of_struct='column')