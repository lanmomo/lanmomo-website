#!/usr/bin/env python3
import os
import sys
import json
import re
import hashlib
import uuid

from datetime import datetime

from flask import Flask, send_from_directory, jsonify, request, session, redirect

from sqlalchemy import or_

from database import db_session, init_db, init_engine

from models import Ticket, User, Payment, Team, TeamUser

import mail
from paypal import Paypal

from paypalrestsdk import Payment as PaypalPayment

ERR_INVALID_PAYPAL = """\
Votre paiement n'a pas pu être vérifié ! Confirmez cette information sur
 votre compte et contactez info@lanmomo.org ."""

ERR_CREATE_PAYPAL = """\
Votre paiement n'a pas pu être créé ! Veuillez réessayer et contactez
 info@lanmomo.org si la situation persiste."""

ERR_EXPIRED = """\
Votre réservation de billet a expirée ! Aucun montant ne vous a été facturé."""

ERR_COMPLETION = """\
Une erreur est survenue lors de la mise à jour de votre billet."""

MSG_SUCCESS_PAY = """\
Félicitations, votre billet est maintenant payé !"""

app = Flask(__name__)


def validate_signup_body(req):
    needed = ['password', 'username', 'firstname',
              'lastname', 'email', 'phone']
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


def team_exists(game, team):
    return Team.query.filter(Team.game == game) \
        .filter(Team.name == team).count() > 0


def captain_has_team(game, captain_id):
    return Team.query.filter(Team.game == game) \
        .filter(Team.captain_id == captain_id).count() > 0


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


@app.route('/api/tournaments', methods=['GET'])
def get_tournaments():
    return jsonify(tournaments), 200


@app.route('/api/teams', methods=['GET'])
def get_all_teams():
    pub_teams = []
    teams = Team.query.all()

    for team in teams:
        pub_teams.append(team.as_pub_dict())
    return jsonify({'teams': pub_teams}), 200


# TODO check if the game exists before creating a team
@app.route('/api/teams', methods=['POST'])
def add_team():
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']

    req = request.get_json()

    team = Team(req['name'], req['game'], user_id)
    if team_exists(team.game, team.name) or \
            captain_has_team(team.game, team.captain_id):
        return jsonify({'message': "Vous avez déja une équipe pour ce jeu " +
                        "ou le nom d'équipe est deja utilisé"}), 400

    db_session.add(team)
    db_session.commit()
    return jsonify({'message': 'Team Created'}), 200


@app.route('/api/teams/<id>', methods=['DELETE'])
def delete_team(id):
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']

    team = Team.query.filter(Team.id == id).first()
    if not team:
        return jsonify({'message': 'no team found'}), 500

    if team.captain_id != user_id:
        return jsonify({'message':
                        "Vous n'êtes pas le capitaine de cette équipe"}), 401
    else:
        db_session.delete(team)
        db_session.commit()
        return jsonify({'message': 'Team Deleted!'}), 200


@app.route('/api/servers', methods=['GET'])
def get_servers():
    return jsonify({'error': 'Not implemented'}), 500


@app.route('/api/servers', methods=['POST'])
def update_server():
    return jsonify({'error': 'Not implemented'}), 500


def get_ticket_from_seat_num(seat_num):
    ticket = Ticket.query \
        .filter(Ticket.seat_num == seat_num) \
        .filter(or_(Ticket.paid,
                    Ticket.reserved_until >= datetime.now())).first()
    return ticket


@app.route('/api/tickets/seat/<seat_num>/free', methods=['GET'])
def seat_is_free(seat_num):
    ticket = get_ticket_from_seat_num(seat_num)
    if ticket:
        user = User.query.filter(User.id == ticket.owner_id).first()
        return jsonify({
            'free': False,
            'ticket': ticket.as_pub_dict(),
            'user': user.as_pub_dict()}
        ), 200
    return jsonify({'free': True}), 200


@app.route('/api/tickets/seat/<seat_num>', methods=['GET'])
def ticket_from_seat(seat_num):
    ticket = get_ticket_from_seat_num(seat_num)

    if ticket:
        return jsonify({'ticket': seat.as_pub_dict()}), 200
    return jsonify({}), 404


@app.route('/api/tickets/type/<type_id>', methods=['GET'])
def get_tickets_by_type(type_id):
    pub_tickets = []
    tickets = Ticket.query \
        .filter(Ticket.type_id == type_id) \
        .filter(or_(Ticket.paid, Ticket.reserved_until >= datetime.now())).all()

    pub = map(lambda ticket: ticket.as_pub_dict(), tickets)
    return jsonify({'tickets': list(pub)}), 200


@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    tickets = Ticket.query.filter(
        or_(
            Ticket.paid,
            Ticket.reserved_until >= datetime.now())).all()

    pub = map(lambda ticket: ticket.as_pub_dict(), tickets)
    return jsonify({'tickets': list(pub)}), 200


@app.route('/api/tickets', methods=['POST'])
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
    seat_num = None
    if ticket_type == app.config['TYPE_IDS']['pc']:
        if 'seat' not in req:
            return bad_request()
        seat_num = req['seat']

    tickets_max = app.config['TICKETS_MAX']
    price = app.config['PRICING'][ticket_type]

    r = Ticket.book_temp(user_id, ticket_type, price, tickets_max, seat_num)

    if r[0]:
        ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
            .filter(or_(Ticket.paid, Ticket.reserved_until >= datetime.now())) \
            .one()
        return jsonify({'ticket': ticket.as_pub_dict()}), 201

    # Conflict while booking ticket
    return jsonify({'error': str(r[1])}), 409


@app.route('/api/tickets/pay', methods=['POST'])
def pay_ticket():
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']

    req = request.get_json()
    if 'discount_momo' in req:
        discount = app.config['DISCOUNT_MOMO']
    else:
        discount = 0

    try:
        ticket = Ticket.query.filter(Ticket.owner_id == user_id).one()

        # Update ticket with discount and total
        ticket.discount_amount = discount
        ticket.total = ticket.price - discount

        db_session.add(ticket)
        db_session.commit()

        paypal_payment = paypal_api.create(ticket)
        payment = Payment(
            amount=ticket.total, ticket_id=ticket.id,
            paypal_payment_id=paypal_payment['paypal_payment_id'])

        db_session.add(payment)
        db_session.commit()

        # TODO send email with paypal url

        return jsonify({'redirect_url': paypal_payment['redirect_url']}), 201
    except Exception as e:
        # TODO log error
        print(str(e))
        return jsonify({
            'error': 'Une erreur est survenue lors de la création de' +
            ' paiement'}), 500


def err_execute_and_complete_payment(paypal_payment_id, paypal_payer_id):
    """"Returns ERROR or None"""
    # lock table tickets
    db_session.execute('LOCK TABLES tickets WRITE, payments WRITE;')

    payment = get_og_payment(paypal_payment_id)
    if not payment:
        return jsonify({'message': 'aucun paiement'}), 404

    ticket = get_ticket_from_payment(payment)

    err = get_err_from_ticket(ticket)
    if err:
        return err

    prepare_payment_execution(payment, paypal_payer_id, ticket)

    # Unlock tables (we do not want to lock while we query the paypal api)
    db_session.execute('UNLOCK TABLES;')

    paypal_payment = PaypalPayment.find(paypal_payment_id)
    # Execute the payment
    if (not paypal_payment.execute({"payer_id": paypal_payer_id}) or
            paypal_payment.state.lower() != 'approved'):
        # Could not execute or execute did not approve transaction
        return jsonify({'message': ERR_INVALID_PAYPAL}), 402

    # Validate payment is created
    paypal_payment = PaypalPayment.find(paypal_payment_id)
    if paypal_payment.state.lower() != 'created':
        return jsonify({'message': ERR_CREATE_PAYPAL}), 402

    return complete_purchase(ticket)


@app.route('/api/tickets/pay/execute', methods=['PUT'])
def execute_payment():
    req = request.get_json()
    paypal_payment_id = req['payment_id']
    payer_id = req['payer_id']

    try:
        err = err_execute_and_complete_payment(paypal_payment_id, payer_id)
        if err:
            db_session.rollback()
            db_session.execute('UNLOCK TABLES;')
            return err

        # Success
        return jsonify({'message': MSG_SUCCESS_PAY}), 200
    except Exception as e:
        try:
            db_session.rollback()
            # try to unlock table
            db_session.execute('UNLOCK TABLES;')
        except:
            pass
        # TODO logging and error redirect
        print(e)
        return jsonify({'error': 'Une erreur inconnue est survenue.'}), 500


def get_og_payment(paypal_payment_id):
    try:
        return Payment.query.filter(
            Payment.paypal_payment_id == paypal_payment_id).one()
    except:
        return None


def get_ticket_from_payment(payment):
    try:
        return Ticket.query.filter(
            Payment.ticket_id == payment.ticket_id).one()
    except:
        return None


def prepare_payment_execution(payment, payer_id, ticket):
    # Set paypal's payer id to payment
    payment.paypal_payer_id = payer_id
    db_session.add(payment)

    # Reserve seat for 30 more seconds if necessary
    # time_after_tran = datetime.now() + timedelta(seconds=30)
    # if ticket.reserved_until <= time_after_tran:
    # TODO set new reservation
    #    pass


def get_err_from_ticket(ticket):
    """Check if the payment is related to a valid reservation"""
    if not ticket:
        return jsonify({'error': 'aucun billet'}), 409

    # Check if ticket is already paid
    if ticket.paid:
        return jsonify({'error': 'Votre billet a déjà été payé !'}), 409

    # Check if reservation is expired
    if ticket.reserved_until < datetime.now():
        return jsonify({'error': ERR_EXPIRED}), 410

    return None


def complete_purchase(ticket):
    try:
        db_session.execute('LOCK TABLES tickets WRITE;')
        # update ticket
        ticket.paid = True
        db_session.add(ticket)
        db_session.commit()

        db_session.execute('UNLOCK TABLES;')
        # TODO send email with payment confirmation
    except:
        return jsonify({'message': ERR_COMPLETION}), 409

    return None


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


@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return login_in_please()

    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()

    if user:
        return jsonify({'user': user.as_private_dict()}), 200
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
    if 'email' not in req or 'password' not in req:
        return bad_request()

    email = req['email']
    password = req['password']

    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify({'error': 'Les informations ne concordent pas !'}), 401

    if not user.confirmed and not app.config['DEBUG']:
        return jsonify({'error': """\
Veuillez valider votre courriel !
 Contactez info@lanmomo.org si le courriel n'a pas été reçu."""}), 400

    if get_hash(password, user.salt) == user.password:
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
    # support html5mode
    if '.' not in path:
        return index()

    return send_from_directory('public', path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def bad_request(message='Les informations sont invalides ou incomplètes.'):
    return jsonify({'message': message}), 400


def login_in_please(message='Vous devez vous connecter.'):
    return jsonify({'message': message}), 401


def setup(conf_path):
    global app, games, tournaments
    app.config.from_pyfile(conf_path)
    init_engine(app.config['DATABASE_URI'])
    init_db()

    paypal_api = Paypal()
    paypal_api.configure(
        client_id=app.config['PAYPAL_API_ID'],
        client_secret=app.config['PAYPAL_API_SECRET'],
        mode=app.config['PAYPAL_API_MODE'])

    with open('config/games.json') as data_file:
        games = json.load(data_file)
    with open('config/tournaments.json') as data_file:
        tournaments = json.load(data_file)
    return app

if __name__ == '__main__':
    setup('config/default_config.py').run(debug=True)
