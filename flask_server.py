import flask
from flask import send_from_directory

from src.Z_methods import consolidate_discoggs_data, request_videos_from_X
from src.DB_Manager import db_manager

app = flask.Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')
# Absolute path to base directory and public directory
BASE_DIR = WD + '/web'

db_conn = db_manager("data/housify.db")


@app.route('/')
def index():
    return send_from_directory(BASE_DIR,'page.html')

@app.route('/web/<path:path>')
def send_static(path):
    print(BASE_DIR + '/' + path)
    return send_from_directory(BASE_DIR, path)

@app.route('/api/get_videos/<search>/<type>/<need_db>')
def receive_json(search, type, need_db):
    data = request_videos_from_X(search, type)
    header, videos = data.get_header_and_data()
    if type =='PLAYLIST': 
        delete_field = 'playlistId'
    elif type == 'USER': 
        delete_field = 'videoOwnerChannelId'
    if need_db == 'true': 
        db_conn.write_db(header, videos, table_name='music', delete_on=[delete_field])
    return {'status': 'success', 'videos': videos, 'header': header, 'count': len(videos)}

@app.route('/api/see_database/')
def see_database():
    header, data = db_conn.read_db(table_name='music')
    return {'status': 'success', 'header': header, 'videos': data}

# @app.route('/api_dev/consolidate_discogs_data/<max_results>/<overwrite_db>')
# def consolidate_discogs(max_results, overwrite_db):
#     if max_results == 'None': max_results = None
#     data = consolidate_discoggs_data(max_results=max_results, overwrite_db=overwrite_db.lower() == 'true')
#     header, videos = data
#     db_conn.write_db(header, videos, table_name='discogs', delete_on=['id'])
#     return {'status': 'success', 'count': len(videos)}


@app.route('/api_dev/consolidate_discogs_data/send_current_db/')
def send_current_db():
    header, videos = db_conn.read_db(table_name='discogs')
    return {'status': 'success', 'header': header, 'videos': videos, 'count': len(videos)}

if __name__ == '__main__':
    app.run(debug=True, port=5000)