import flask
from flask import send_from_directory
import logging

from src.methods import request_videos_from_X, db_manager

app = flask.Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
WD = os.getenv('WD')
# Absolute path to base directory and public directory
BASE_DIR = WD + '/web'

db_conn = db_manager(BASE_DIR, "data/housify.db")


@app.route('/')
def index():
    return send_from_directory(BASE_DIR + '/index','page.html')

@app.route('/web/<path:path>')
def send_static(path):
    print(BASE_DIR + '/' + path)
    return send_from_directory(BASE_DIR, path)

@app.route('/api/get_videos/<search>/<type>/<need_db>')
def receive_json(search, type, need_db):
    data = request_videos_from_X(search, type)
    logging.info(f"Received request for {type} {search}, returning {data.get_number_of_videos()} videos")
    header, videos = data.get_header_and_data()
    if need_db == 'true': db_conn.write_db(header, videos)
    return {'status': 'success', 'videos': videos, 'header': header, 'count': len(videos)}

@app.route('/api/see_database/')
def see_database():
    header, data = db_conn.read_db(table_name='music')
    return {'status': 'success', 'header': header, 'videos': data}

if __name__ == '__main__':
    app.run(debug=True, port=5000)