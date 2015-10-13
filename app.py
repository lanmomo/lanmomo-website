#!/usr/bin/env python3
import hashlib
import mail
import uuid
import logging
import os

from os.path import isdir, dirname
from datetime import datetime

from flask import Flask, send_from_directory, jsonify, request, session
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler

from paypalrestsdk import Payment as PaypalPayment

from sqlalchemy import or_, not_
from sqlalchemy.orm import contains_eager

from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.lib.units import cm

from database import db_session, init_db, init_engine
from models import Ticket, User, Payment, Team

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


def create_pdf_with_qr(qr_string, filename):
    if not isdir(dirname(filename)):
        os.makedirs(dirname(filename))

    p = canvas.Canvas(filename)
    p.translate(cm * 5, cm * 10)
    qrw = QrCodeWidget(qr_string)
    b = qrw.getBounds()

    w = b[2] - b[0]
    h = b[3] - b[1]

    d = Drawing(240, 240, transform=[240 / w, 0, 0, 240 / h, 0, 0])
    d.add(qrw)

    line1 = """\
Veuillez présenter ce code QR à l'acceuil lors de votre arrivée au LAN."""
    line2 = "Il est recommandé d'enregistrer ce PDF sur un appareil mobile," + \
        " mais il est aussi possible de l'imprimer."
    p.drawCentredString(5 * cm, 15 * cm, line1)
    p.drawCentredString(5 * cm, 16 * cm, line2)

    renderPDF.draw(d, p, 1, 1)
    p.save()


def get_logger():
    return app.logger


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


def send_email(to_email, to_name, subject, message, attachements=None):
    mail.send_email(to_email, to_name, subject, message,
                    app.config['MAILGUN_USER'], app.config['MAILGUN_KEY'],
                    app.config['MAILGUN_DOMAIN'], attachements=attachements)


@app.before_request
def func():
    session.modified = True


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
    return jsonify({'message': 'Not implemented'}), 500


@app.route('/api/servers', methods=['POST'])
def update_server():
    return jsonify({'message': 'Not implemented'}), 500


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
        return jsonify({'ticket': ticket.as_pub_dict()}), 200
    return jsonify({}), 404


@app.route('/api/tickets/type/<type_id>', methods=['GET'])
def get_tickets_by_type(type_id):
    tickets = Ticket.query \
        .join(Ticket.owner) \
        .options(contains_eager(Ticket.owner)) \
        .filter(Ticket.type_id == type_id) \
        .filter(or_(Ticket.paid, Ticket.reserved_until >= datetime.now())) \
        .all()

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


@app.route('/api/tickets/seat', methods=['PUT'])
def change_seat():
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']
    req = request.get_json()

    if 'seat' not in req:
        return bad_request()
    seat_num = req['seat']

    ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
        .filter(Ticket.reserved_until >= datetime.now()).first()

    if not ticket:
        return jsonify({'message':
                       "Votre billet n'existe pas ou est expiré."}), 400

    if ticket.type_id != app.config['TYPE_IDS']['pc']:
        return jsonify({'message': "Votre billet n'est pas de type PC. " +
                       "Veuillez recommencer avec un billet PC."}), 400

    res = None
    try:
        db_session.execute('LOCK TABLES tickets WRITE, users READ;')
        err = change_seat_for_user(user_id, seat_num)

        if err:
            res = err
        else:
            ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
                .filter(Ticket.reserved_until >= datetime.now()) \
                .one()

            db_session.commit()
            res = jsonify({'ticket': ticket.as_pub_dict()}), 200
    except Exception as e:
        app.logger.error('Erreur lors du changement de siège: "%s"' % str(e))
        res = jsonify({'message': 'Erreur inconnue.'}), 500
    finally:
        db_session.execute('UNLOCK TABLES;')

    return res


def change_seat_for_user(user_id, seat_num):
    """Please lock tables before calling. Returns error or None.
    """
    try:
        current_ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
            .filter(Ticket.reserved_until >= datetime.now()) \
            .filter(not_(Ticket.paid)) \
            .one()
    except:
        return jsonify({
            'message': 'Aucun billet valide, billet expiré ou billet déjà payé.'
            }), 409

    wanted_seat_count = Ticket.query \
        .filter(Ticket.seat_num == seat_num) \
        .filter(or_(
            Ticket.paid, Ticket.reserved_until >= datetime.now())) \
        .count()
    if wanted_seat_count > 0:
        return jsonify({'message': 'Ce siège est déjà occupé.'}), 409

    current_ticket.seat_num = seat_num
    db_session.add(current_ticket)


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
    mess = 'Conflit lors de la réservation de billet: "%s"' % str(r[1])
    if len(r) == 3:
        mess = '%s Exception: %s' % (mess, r[2])
    app.logger.error(mess)

    return jsonify({'message': str(r[1])}), 409


@app.route('/api/tickets/pay', methods=['POST'])
def pay_ticket():
    if 'user_id' not in session:
        return login_in_please()
    user_id = session['user_id']

    req = request.get_json()
    if 'discountMomo' not in req or 'participateGG' not in req:
        return bad_request()

    discount = app.config['DISCOUNT_MOMO'] if req['discountMomo'] else 0
    participate_gg = req['participateGG']

    try:
        ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
            .filter(Ticket.reserved_until >= datetime.now()) \
            .one()

        # Update ticket with discount and total
        ticket.discount_amount = discount
        ticket.total = ticket.price - discount

        # Set user's choice to participate in GG's prize pool
        ticket.participate_gg = participate_gg

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
        app.logger.error(
            'Erreur lors de la création de paiment: "%s"' % str(e))
        return jsonify({
            'message': 'Une erreur est survenue lors de la création de' +
            ' paiement'}), 500


@app.route('/api/qr/<qr_token>', methods=['GET'])
def find_ticket_by_qr_token(qr_token):
    try:
        ticket = Ticket.query.filter(
            Ticket.qr_token == qr_token).one().as_private_dict()

        owner = User.query.filter(
            User.id == ticket['owner_id']).one().as_private_dict()
        return jsonify({'ticket': ticket, 'owner': owner}), 200
    except:
        return jsonify({'message': 'aucun billet'}), 404


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

    # Validate payment is created
    paypal_payment = PaypalPayment.find(paypal_payment_id)
    if paypal_payment.state.lower() != 'created':
        app.logger.critical(
            'Possible tentative de fraude: "%s"' % str(paypal_payment))
        return jsonify({'message': ERR_CREATE_PAYPAL}), 402

    # Execute the payment
    if (not paypal_payment.execute({"payer_id": paypal_payer_id}) or
            paypal_payment.state.lower() != 'approved'):
        # Could not execute or execute did not approve transaction
        app.logger.critical(
            'Possible tentative de fraude: "%s"' % str(paypal_payment))
        return jsonify({'message': ERR_INVALID_PAYPAL}), 402

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
        app.logger.error(
            'Exception lors de l\'exécution de paiment: "%s"' % str(e))
        return jsonify({'message': 'Une erreur inconnue est survenue.'}), 500


def get_og_payment(paypal_payment_id):
    try:
        return Payment.query.filter(
            Payment.paypal_payment_id == paypal_payment_id).one()
    except:
        return None


def get_ticket_from_payment(payment):
    try:
        return Ticket.query.filter(
            Payment.ticket_id == payment.ticket_id) \
            .filter(or_(Ticket.paid, Ticket.reserved_until >= datetime.now())) \
            .one()
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
        return jsonify({'message': 'aucun billet'}), 409

    # Check if ticket is already paid
    if ticket.paid:
        return jsonify({'message': 'Votre billet a déjà été payé !'}), 409

    # Check if reservation is expired
    if ticket.reserved_until < datetime.now():
        return jsonify({'message': ERR_EXPIRED}), 410

    return None


def complete_purchase(ticket):
    try:
        db_session.execute('LOCK TABLES tickets WRITE, payments WRITE;')
        # update ticket
        ticket.paid = True
        db_session.add(ticket)
        db_session.commit()

        db_session.execute('UNLOCK TABLES;')

        # Temp file for the PDF
        ticket_pdf_filename = '/tmp/lanmomo_pdf/%s/billet.pdf' % ticket.qr_token
        # Create PDF with the QR code linking to online verification
        create_pdf_with_qr('https://lanmomo.org/qr/%s' % ticket.qr_token,
                           ticket_pdf_filename)

        # Find ticket owner to send email to
        user = User.query.filter(User.id == ticket.owner_id).one()
        fullname = '%s %s' % (user.firstname, user.lastname)
        subject = 'Confirmation de votre achat de billet du LAN Montmorency'
        attachements = [ticket_pdf_filename]
        message = 'va voir tes pièces jointes le gros'  # TODO

        # Send email with payment confirmation
        send_email(user.email, fullname, subject, message, attachements)
    except Exception as e:
        app.logger.error(
            'Erreur lors de la fermeture de la commande pour ' +
            'le billet "%s"!: "%s"'
            % (ticket, str(e)))
        return jsonify({'message': ERR_COMPLETION}), 409

    return None


@app.route('/api/users/ticket', defaults={'user_id': None})
@app.route('/api/users/<user_id>/ticket', methods=['GET'])
def get_ticket_from_user(user_id):
    if not user_id:
        if 'user_id' not in session:
            return bad_request()
        user_id = session['user_id']
        owner = True

    ticket = Ticket.query.filter(Ticket.owner_id == user_id) \
        .filter(or_(Ticket.paid, Ticket.reserved_until >= datetime.now())) \
        .first()
    if not ticket:
        return jsonify({}), 200
    if owner:
        return jsonify({'ticket': ticket.as_private_dict()}), 200
    return jsonify({'ticket': ticket.as_pub_dict()}), 200


@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return login_in_please()

    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()

    if user:
        return jsonify({'user': user.as_private_dict()}), 200
    return jsonify({'message': 'Non authorisé'}), 403


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
        return jsonify({'message': 'Les informations ne concordent pas !'}), 401

    if not user.confirmed and not app.config['DEBUG']:
        return jsonify({'message': """\
Veuillez valider votre courriel !
 Contactez info@lanmomo.org si le courriel n'a pas été reçu."""}), 400

    if get_hash(password, user.salt) == user.password:
        session['user_id'] = user.id
        return jsonify({'success': True})

    return jsonify({'message': 'Les informations ne concordent pas !'}), 401


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
    conf_url = 'https://lanmomo.org/verify/%s' % user.confirmation_token

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


@app.route('/api/users', methods=['PUT'])
def mod_user():
    if 'user_id' not in session:
        return login_in_please()

    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).one()

    has_update = False
    req = request.get_json()
    mod_keys = ['lastname', 'firstname', 'email', 'username', 'phone']

    for mod_key in mod_keys:
        if mod_key in req and getattr(user, mod_key) != req[mod_key]:
            if mod_key == 'email' and email_exists(req['email']):
                return jsonify({'Courriel déjà utilisé.'}), 409
            if mod_key == 'username' and username_exists(req['username']):
                return jsonify({'Pseudonyme déjà utilisé.'}), 409
            has_update = True
            setattr(user, mod_key, req[mod_key])

    if 'password' in req and 'oldPassword' in req:
        if get_hash(req['oldPassword'], user.salt) != user.password:
            return jsonify({'message': 'Mauvais mot de passe actuel.'}), 400
        user.password = get_hash(req['password'], user.salt)
        has_update = True

    if has_update:
        db_session.add(user)
        db_session.commit()
        return jsonify({'user': user.as_private_dict()}), 200

    return jsonify({'message': 'Aucune information différente.'}), 400


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
    global app, paypal_api
    app.config.from_pyfile(conf_path)

    log_path = app.config['LOG_PATH']
    handler = TimedRotatingFileHandler(
        log_path, utc=True, when='D', backupCount=365 * 2)

    handler.setLevel(logging.INFO)
    handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)

    app.logger.info('Starting lanmomo app')

    init_engine(app.config['DATABASE_URI'])
    init_db()

    paypal_api = Paypal()
    paypal_api.configure(
        client_id=app.config['PAYPAL_API_ID'],
        client_secret=app.config['PAYPAL_API_SECRET'],
        mode=app.config['PAYPAL_API_MODE'],
        return_url=app.config['PAYPAL_RETURN_URL'],
        cancel_url=app.config['PAYPAL_CANCEL_URL'])
    return app

if __name__ == '__main__':
    setup('config/default_config.py').run(debug=True)
