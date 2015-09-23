#!/usr/bin/env python3
import os
import sys
import json
import re
import hashlib

from flask import Flask, send_from_directory, jsonify, request
from database import db_session, init_db, init_engine
from models import Subscription, User

app = Flask(__name__)


def get_hash(password, salt):
    m = hashlib.sha512()
    m.update(salt.encode('utf8'))
    m.update(password.encode('utf8'))
    return m.digest()


def email_exists(email):
    return User.query.filter(User.username == email).count() > 0


def username_exists(username):
    return User.query.filter(User.username == username).count() > 0


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

    return jsonify({'exists': username_exists(req['username'])}), 200


@app.route('/api/users/has/email', methods=['POST'])
def has_email():
    req = request.get_json()
    if 'email' not in req:
        return bad_request()

    return jsonify({'exists': email_exists(req['email'])}), 200


def validate_signup_body(req):
    needed = ['password', 'username', 'firstname', 'lastname', 'email', 'phone']
    for n in needed:
        if n not in req.keys():
            return False
    return True


@app.route('/api/users', methods=['POST'])
def signup():
    req = request.get_json()
    if not validate_signup_body(req):
        return bad_request()

    if email_exists(req['email']) or username_exists(req['username']):
        return bad_request('Courriel ou utilisateur déjà pris !')

    salt = "salty"
    hashpass = get_hash(req['password'], salt)

    user = User(username=req['username'], firstname=req['firstname'],
                lastname=req['lastname'], email=req['email'],
                phone=req['phone'], password=hashpass, salt=salt)
    db_session.add(user)
    db_session.commit()

    # TODO send email confirmation
    return jsonify({'message': 'Vérifier le courriel. TODO'}), 200


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


def bad_request(custom_message):
    message = 'Les informations données sont invalides ou incomplètes'
    if custom_message:
        message = custom_message
    return jsonify({'message': message}), 400


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
