#!/usr/bin/env python3
import os
import sys
import json
import re
import hashlib
import uuid

from smtplib import SMTP
from email.mime.text import MIMEText
from flask import Flask, send_from_directory, jsonify, request, session

import mail
from database import db_session, init_db, init_engine
from models import Ticket, Seat, User

app = Flask(__name__)


def validate_signup_body(req):
    needed = ['password', 'username', 'firstname', 'lastname', 'email', 'phone']
    for n in needed:
        if n not in req.keys():
            return False
    return True


def get_hash(password, salt):
    m = hashlib.sha512()
    m.update(salt.encode('utf8'))
    m.update(password.encode('utf8'))
    return m.digest()


def email_exists(email):
    return User.query.filter(User.email == email).count() > 0


def username_exists(username):
    return User.query.filter(User.username == username).count() > 0


def send_email(to_email, to_name, subject, message):
    mail.send_email(to_email, to_name, subject, message,
                    app.config['MAILGUN_USER'], app.config['MAILGUN_KEY'],
                    app.config['MAILGUN_DOMAIN'])


@app.before_request
def func():
    session.modified = True


@app.route('/api/games', methods=['GET'])
def get_games():
    return jsonify(games), 200


@app.route('/api/servers', methods=['GET'])
def get_servers():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/servers', methods=['POST'])
def update_server():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/ticket', methods=['POST'])
def book_ticket():
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']

    req = request.get_json()
    if 'type' not in req:
        return bad_request()
    ticket_type = req['type']

    if ticket_type not in app.config['TYPE_IDS'].values():
        return bad_request()

    if ticket_type == app.config['TYPE_IDS']['pc']:
        if 'seat' not in req:
            return bad_request()
        seat = req['seat']
    else:
        seat = None

    tickets_max = app.config['TICKETS_MAX']

    try:
        if Ticket.book_synced(user_id, ticket_type, tickets_max, seat):
            ticket = Ticket.query.filter(Ticket.owner_id == user_id).one()
            return jsonify({'ticket': ticket.as_pub_dict()}), 201

        return jsonify({'error': 'Une erreur inconnue est survenue.'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 409  # Conflit


@app.route('/api/users/ticket', defaults={'user_id': None})
@app.route('/api/users/<user_id>/ticket', methods=['GET'])
def get_ticket_from_user(user_id):
    if not user_id:
        if 'user_id' not in session:
            return bad_request()
        user_id = session['user_id']

    ticket = Ticket.query.filter(Ticket.owner_id == user_id).first()
    if not ticket:
        return jsonify({}), 200

    return jsonify({'ticket': ticket.as_pub_dict()}), 200


@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    pub_tickets = []
    tickets = Ticker.query.all()

    for ticket in tickets:
        pub_tickets.append(ticket.as_pub_dict())
    return tickets


@app.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()

    if user:
        return jsonify({'user': user.as_pub_dict()}), 200
    return jsonify({'error': 'Non authorisé'}), 403


@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200


@app.route('/api/login', methods=['GET'])
def is_logged_in():
    return jsonify({'logged_in': 'user_id' in session}), 200


@app.route('/api/login', methods=['POST'])
def login():
    req = request.get_json()
    if 'password' not in req or 'password' not in req:
        return bad_request()

    email = req['email']
    password = req['password']

    user = User.query.filter(User.email == email).first()

    if not user.confirmed and not app.config['DEBUG']:
        return jsonify({'error': """\
Veuillez valider votre courriel !
 Contactez info@lanmomo.org si le courriel n'a pas été reçu."""}), 400

    if user and get_hash(password, user.salt) == user.password:
        session['user_id'] = user.id
        return jsonify({'success': True})

    return jsonify({'error': 'Les informations ne concordent pas !'}), 401


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


@app.route('/api/verify/<token>', methods=['GET'])
def verify_user_email(token):
    user = User.query.filter(User.confirmation_token == token).first()
    if not user:
        return bad_request('Mauvais jeton fournis !')

    if user.confirmed:
        return jsonify({'first': False}), 200

    user.confirmed = True
    db_session.add(user)
    db_session.commit()
    return jsonify({'first': True}), 200


@app.route('/api/users', methods=['POST'])
def signup():
    req = request.get_json()
    if not validate_signup_body(req):
        return bad_request()

    if email_exists(req['email']) or username_exists(req['username']):
        return bad_request('Courriel ou utilisateur déjà pris !')

    salt = uuid.uuid4().hex
    hashpass = get_hash(req['password'], salt)

    user = User(username=req['username'], firstname=req['firstname'],
                lastname=req['lastname'], email=req['email'],
                phone=req['phone'], password=hashpass, salt=salt)
    db_session.add(user)
    db_session.commit()

    user = User.query.filter(User.email == req['email']).one()

    fullname = '%s %s' % (req['firstname'], req['lastname'])
    conf_url = 'https://lanmomo.org/verify/%s' % \
        user.confirmation_token

    message = ("""\
Bonjour %s, <br><br>
Veuillez confirmer votre courriel en visitant le lien suivant:
 <a href="%s">%s</a><br><br>
Merci et à bientôt !<br><br>
<small>Ceci est un courriel envoyé automatiquement.
 Veuillez ne pas y répondre.</small>""") \
        % (fullname, conf_url, conf_url)
    subject = 'Confirmation de votre compte LAN Montmorency'

    if not app.config['DEBUG']:
        send_email(req['email'], fullname, subject, message)

    return jsonify({'message': """\
Un message de confirmation a été envoyé à votre adresse courriel. Si le message
 n'est pas reçu dans les prochaines minutes, vérifiez vos pourriel !"""}), 201


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def bad_request(message='Les informations sont invalides ou incomplètes.'):
    return jsonify({'message': message}), 400


def login_in_please(message='Vous devez vous connecter.'):
    return jsonify({'message': message}), 401


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
