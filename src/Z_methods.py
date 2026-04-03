import sys

sys.path.append('src')

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("YTB_API")
BASE_DIR = os.getenv('WD')

from API_Youtube import High_level_API

def request_videos_from_X(search, type, max_results = 50, max_output_length=None): 
    api = High_level_API(api_key)
    res = api.get_all_videos(search, type=type, max_results=max_results, max_output_length=max_output_length)
    return res

def consolidate_discoggs_data(max_results=None, overwrite_db=False):
    import time
    from API_Discogs import Mid_level_API
    from JSON_Global_SingleLayer import SingleLayerDataNormalizer
    from DB_Manager import db_manager
    data_normalizer = SingleLayerDataNormalizer()
    conn = db_manager()
    api_key = "DEVELOPER_KEY"
    api = Mid_level_API(api_key)
    if overwrite_db: condition = '1=1'
    else: condition = "Discogged IS NULL OR Discogged != 'Y'"
    header, data = conn.read_db(query=f"select title, etag from music where {condition};")
    if not max_results : max_results = len(data)
    for i in data[:max_results]:
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

if __name__ == "__main__":
    consolidate_discoggs_data(max_results=10, overwrite_db=True)