#!/usr/bin/env python3
import os
import sys
import json
import re

from flask import Flask, send_from_directory, jsonify, request
from database import db_session, init_db, init_engine
from models import Subscription, User

app = Flask(__name__)


@app.route('/api/games', methods=['GET'])
def get_games():
    return jsonify(games), 200


@app.route('/api/servers', methods=['GET'])
def get_servers():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/servers', methods=['POST'])
def update_server():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/users/has/username', methods=['POST'])
def has_username():
    req = request.get_json()
    if 'username' not in req:
        return bad_request()

    exists = User.query.filter(User.username == req['username']).count() > 0
    return jsonify({'exists': exists}), 200


@app.route('/api/users/has/email', methods=['POST'])
def has_email():
    req = request.get_json()
    if 'email' not in req:
        return bad_request()

    exists = User.query.filter(User.email == req['email']).count() > 0
    return jsonify({'exists': exists}), 200


@app.route('/api/subscribe', methods=['POST'])
def sub():
    req = request.get_json()
    if 'email' in req:
        email = req['email']
        match = re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                          email)
        if match:
            return subscribe_email(email)
        else:
            return bad_request()
    return bad_request()


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def bad_request():
    return jsonify({'message': 'Les informations données sont invalides ou ' +
                    'incomplètes'}), 400


def subscribe_email(email):
    if Subscription.query.filter(Subscription.email == email).count() == 0:
        sub = Subscription(email)
        db_session.add(sub)
        db_session.commit()
        return jsonify({'message': 'Votre courriel a été ajouté sur la liste.' +
                        'Vous receverez un courriel dès que les billets ' +
                        'seront en vente !'}), 200
    else:
        return jsonify({'message': 'Votre courriel est déjà la liste ! ' +
                        'Vous receverez un courriel dès que les billets ' +
                        'seront en vente !'}), 200


def setup(conf_path):
    global app, games
    app.config.from_pyfile(conf_path)
    init_engine(app.config['DATABASE_URI'])
    init_db()

    with open('config/games.json') as data_file:
        games = json.load(data_file)
    return app

if __name__ == '__main__':
    setup('config/default_config.py').run(debug=True)
