import flask
from flask import send_from_directory, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from src.Z_methods import request_videos_from_X, Cred_inator, get_field
from src.DB_Manager import db_manager
from src.DB_UserManager import DB_UserManager
app = flask.Flask(__name__)
logging.basicConfig(level=logging.INFO)
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
link_users = Cred_inator()

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
    if need_db == 'true': 
        db_conn.write_db(header, videos, table_name='music', delete_on=[delete_field])
    return {'status': 'success', 'videos': videos, 'header': header, 'count': len(videos)}

@app.route('/api/see_database/')
def see_database():
    header, data = db_conn.read_db(table_name='music')
    print(data)
    return {'status': 'success', 'header': header, 'videos': data}


@app.route('/api/consolidated_data/send_musicdiscg/')
def send_current_db():
    header, videos = db_conn.read_db(table_name='musicdisg')
    return {'status': 'success', 'header': header, 'videos': videos, 'count': len(videos)}

@app.route('/api/login/', methods=['POST'])
def login():
    data = flask.request.get_json()
    username = data.get('username')
    password = data.get('password')
    db_user_manager = DB_UserManager(BDD_URL)
    password_hash = db_user_manager.get_password_hash(username)
    if password_hash is not None and check_password_hash(password_hash, password):
        link_users.create_passphrase_for_user(username)
        return {'status': 'success', 'message': 'Login successful.', 'passphrase': link_users.get_passphrase(username)}
    elif password_hash is None:
        res = db_user_manager.add_user(username, generate_password_hash(password))
        if res:
            return {'status': 'success', 'message': 'User registered.'}
        else :
            return {'status': 'error', 'message': 'Registration failed.'}
    else:
        return {'status': 'error', 'message': 'Invalid credentials.'}

@app.route('/api/get_rated_videos/<passphrase>')
def get_rated_video(passphrase):
    user = link_users.get_user(passphrase)
    if user is None:
        return {'status': 'error', 'message': 'Invalid passphrase.'}
    else:
        query = f"select etag, music_id, music_title, music_url, "+'"user_rating"'+f", user_Category, rating, publishedAt as rating_date from unrated_music WHERE rater_username like '%%{user}%%';"
        print(query)
        header, data = db_conn.read_db(query=query)
        if len(data) == 0:
            return {'status': 'success', 'message': 'No rated videos found.', 'videos': None}
        else:
            return {'status': 'success', 'videos': data, 'header': header}

@app.route('/api/get_unrated_video/<passphrase>', methods=['POST'])
def get_unrated_video(passphrase):
    user = link_users.get_user(passphrase)
    if user is None:
        return {'status': 'error', 'message': 'Invalid passphrase.'}
    else:
        order_by = get_field(flask.request.get_json().get('order_by'))
        query = f"select etag, music_id, music_title, music_url from unrated_music WHERE rater_username not like '%%{user}%%' or rater_username is null {'order by '+order_by if order_by else ''} limit 1;"
        print(query)
        header, data = db_conn.read_db(query=query)
        if len(data) == 0:
            return {'status': 'success', 'message': 'No unrated videos left.', 'video': None}
        else:
            video = data[0]
            return {'status': 'success', 'video': video, 'header': header}

@app.route('/api/submit_rating/', methods=['POST'])
def submit_rating():
    data = flask.request.get_json()
    passphrase = data.get('passphrase')
    etag = data.get('etag')
    rating = data.get('rating')
    SelectedTiles = data.get('SelectedTiles')
    user = link_users.get_user(passphrase)
    if user is None:
        return {'status': 'error', 'message': 'Invalid passphrase.'}
    else:
        db_conn.write_db(header=['etag', 'username', 'rating', 'selectedtiles'], 
                         data=[etag,  user, rating, SelectedTiles], 
                         table_name='USER_RATING',
                         delete_on=['etag', 'username'],
                         type_of_struct='column')
        return {'status': 'success', 'message': 'Rating submitted.'}

@app.route('/api/add_tile/', methods=['POST'])
def add_tile():
    data = flask.request.get_json()
    title = data.get('title')
    db_conn.write_db(header=['tile_name'], 
                         data=[title], 
                         table_name='tiles',
                         delete_on=['tile_name'],
                         type_of_struct='column')
    res = db_conn.read_db(query=f"select tile_name from tiles")
    return {'status': 'success', 'message': 'Tile added.', 'active_tiles': res[1]}

@app.route('/api/remove_tile/<tile_name>')
def remove_tile(tile_name):
    db_conn.modifify_data(data=[tile_name], header=['tile_name'], table_name='tiles', type='delete', on=['tile_name'], type_of_struct='column')
    res = db_conn.read_db(query=f"select tile_name from tiles")
    return {'status': 'success', 'message': 'Tile removed.', 'active_tiles': res[1]}

@app.route('/api/get_tiles/')
def get_tiles():
    res = db_conn.read_db(query=f"select tile_name from tiles")
    return {'status': 'success', 'active_tiles': res[1]}

@app.route('/api/check_passphrase/', methods=['POST'])
def check_passphrase():
    data = flask.request.get_json()
    passphrase = data.get('passphrase')
    user = link_users.get_user(passphrase)
    if user is None:
        return {'status': 'error', 'message': 'Invalid passphrase.'}
    else:
        return {'status': 'success', 'message': 'Valid passphrase.'}

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)