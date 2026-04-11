import sys
sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 encoding for console output
from JSON_Global_Multilayer import JSON_Global_Multilayer

sys.path.append('src')

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("YTB_API")
BASE_DIR = os.getenv('WD')

from API_Youtube import High_level_API
import time
from API_Discogs import Mid_level_API
from JSON_Discord_SingleLayer import SingleLayerDataNormalizer
from DB_JsonHandler import DB_JsonHandler
from DB_Manager import db_manager
from tqdm import tqdm


def request_videos_from_X(search, type, max_results = 50, max_output_length=None): 
    api = High_level_API(api_key)
    res = api.get_all_videos(search, type=type, max_results=max_results, max_output_length=max_output_length)
    return res

def consolidate_discoggs_data(max_results=None, overwrite_db=False):
    data_normalizer = SingleLayerDataNormalizer()
    conn = db_manager()
    api_key = "DEVELOPER_KEY"
    api = Mid_level_API(api_key)
    if overwrite_db: condition = '1=1'
    else: condition = "Discogged IS NULL OR Discogged != 'Y'"
    header, data = conn.read_db(query=f"select title, etag from music where {condition};")
    if max_results is None: max_results = len(data)
    for i in tqdm(data[:max_results], desc="Processing"):
        time.sleep(1)
        releases = api.get_release_id(q=i[0])
        data_normalizer(releases, added_key='etag', added_value=i[1])
        max_results -= 1
        if max_results == 0:
            break
    conn.modifify_data(type='update'
                       , table_name='music'
                       , on=['title']
                       , data=data
                       , header=header
                       , update_values={'Discogged': 'Y'})
    
    return data_normalizer.get_header_and_data()

def import_discord_database():
    api = Mid_level_API(api_key)
    conn = db_manager()
    json_conn = DB_JsonHandler()
    header, data = conn.read_db(query=f"select distinct id from discogs where id not in (select id_main from discogs_main);")
    serializer = JSON_Global_Multilayer( identifier='id')
    for i in tqdm(data):
        try :
            time.sleep(0.5)
            res = api.get_all_data(i[0])
        except Exception as e:
            time.sleep(1)
            print(f"Error fetching data for id {i[0]}: {e}")
            break
        if res :
            res = serializer.walker(res, table_name='discogs_main')
            json_conn.create_table(res)
            try :
                json_conn.insert_data(res, key='id_main') 
            except Exception as e:
                print(f"Error inserting data for id {i[0]}: {e}")
    

if __name__ == '__main__':
    import_discord_database()