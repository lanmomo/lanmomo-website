import os
import sys
import json

from flask import Flask, send_from_directory, jsonify
from database import db_session, init_db, init_engine

app = Flask(__name__)

with open('config/games.json') as data_file:
    games = json.load(data_file)


@app.route('/api/games', methods=['GET'])
def get_games():
    return jsonify(games), 200


@app.route('/api/servers', methods=['GET'])
def get_servers():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/servers', methods=['POST'])
def update_server():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def setup(conf_path):
    global app
    app.config.from_pyfile(conf_path)
    init_engine(app.config['DATABASE_URI'])
    init_db()
    return app

if __name__ == '__main__':
    setup('config/default_config.py').run()
