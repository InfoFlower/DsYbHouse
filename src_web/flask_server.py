import flask
from flask import send_from_directory, redirect, url_for
import logging
from src.Z_methods import request_videos_from_X
from src.DB_Manager import db_manager
app = flask.Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
import os
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
# Absolute path to base directory and public directory
BASE_DIR = WD + 'web/'
BDD_URL = f"postgresql://{DB_USER}:{DB_PASS}@db:5432/{DB_NAME}"

db_conn = db_manager(BDD_URL)

@app.route('/')
def index():
    return redirect(url_for('send_static', path='index/page.html'))

    
@app.route('/web/<path:path>')
def send_static(path):
    logging.debug('requested path: ' + path)
    if len(path.split('/')) > 1:
        return send_from_directory(BASE_DIR, path)
    else :
        return send_from_directory(BASE_DIR, 'index/'+path)

@app.route('/api/get_videos/<search>/<type>/<need_db>')
def receive_json(search, type, need_db):
    data = request_videos_from_X(search, type)
    header, videos = data.get_header_and_data()
    if type =='PLAYLIST': 
        delete_field = 'playlistId'
    elif type == 'USER': 
        delete_field = 'videoOwnerChannelId'
    # if need_db == 'true': 
    #     db_conn.write_db(header, videos, table_name='music', delete_on=[delete_field])
    return {'status': 'success', 'videos': videos, 'header': header, 'count': len(videos)}

@app.route('/api/see_database/')
def see_database():
    header, data = db_conn.read_db(table_name='music')
    return {'status': 'success', 'header': header, 'videos': data}


@app.route('/api/consolidated_data/send_musicdiscg/')
def send_current_db():
    header, videos = db_conn.read_db(table_name='musicdisg')
    return {'status': 'success', 'header': header, 'videos': videos, 'count': len(videos)}

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)