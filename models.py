import uuid

from datetime import datetime, timedelta

from sqlalchemy import Table, Column, Integer, String, Binary, Boolean, \
    ForeignKey, DateTime, Float, text, or_
from sqlalchemy.orm import mapper, relationship

from database import metadata, db_session


class User():
    query = db_session.query_property()

    def __init__(self, username, firstname, lastname, email, phone,
                 password, salt):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.password = password
        self.salt = salt
        self.created_date = datetime.now
        self.confirmed = False
        self.confirmation_token = uuid.uuid4().hex

    def __repr__(self):
        return '<User %r>' % (self.username)

    def from_token(token):
        if token:
            return User.query.filter(
                User.login_token == token).first()

    def as_pub_dict(self):
        pub_dict = {
            'id': self.id,
            'username': self.username
            }
        return pub_dict

    def as_private_dict(self):
        priv_dict = {
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at
            }
        return priv_dict


class Ticket():
    query = db_session.query_property()

    def __init__(self, type_id, owner_id, price, paid=False,
                 reserved_until=None, reserved_at=None, seat_num=None):
        self.type_id = type_id
        self.owner_id = owner_id
        self.price = price
        self.paid = paid
        self.reserved_until = reserved_until
        self.reserved_at = reserved_at
        self.seat_num = seat_num
        self.qr_token = uuid.uuid4().hex

    def __repr__(self):
        return '<Ticket %r>' % (self.id)

    def as_pub_dict(self):
        pub_dict = {
            'type_id': self.type_id,
            'owner_id': self.owner_id,
            'paid': self.paid,
            'reserved_until': self.reserved_until.strftime('%Y-%m-%dT%H:%M:%S'),
            'price': self.price,
            'discount_amount': self.discount_amount,
            'total': self.total
            }
        if self.seat_num:
            pub_dict['seat_num'] = self.seat_num
        if self.owner:
            pub_dict['owner_username'] = self.owner.username
        return pub_dict

    def as_private_dict(self):
        priv_dict = self.as_pub_dict()
        priv_dict['qr_token'] = self.qr_token
        return priv_dict

    def book_temp(user_id, ticket_type, price, tickets_max, seat_num=None):
        try:
            db_session.execute('LOCK TABLES tickets WRITE;')

            # Get reservation and paid ticket total count for user
            user_ticket_count = Ticket.query \
                .filter(Ticket.owner_id == user_id) \
                .filter(or_(
                    Ticket.paid, Ticket.reserved_until >= datetime.now())) \
                .count()

            # Check if user can order a ticket
            if user_ticket_count > 0:
                db_session.rollback()
                db_session.execute('UNLOCK TABLES;')
                return False, \
                    'Vous avez déjà un billet ou une réservation en cours !'

            # Get reservation and paid ticket total count for ticket type
            ticket_type_count = Ticket.query \
                .filter(Ticket.type_id == ticket_type) \
                .filter(or_(
                    Ticket.paid, Ticket.reserved_until >= datetime.now())) \
                .count()

            # Check if more tickets is allowed for this type
            if ticket_type_count >= tickets_max[ticket_type]:
                db_session.rollback()
                db_session.execute('UNLOCK TABLES;')
                return False, \
                    'Le maximum de billet a été réservé pour le moment !'

            # Check if seat is taken
            if seat_num:
                wanted_seat_count = Ticket.query \
                    .filter(Ticket.seat_num == seat_num) \
                    .filter(or_(
                        Ticket.paid, Ticket.reserved_until >= datetime.now())) \
                    .count()
                if wanted_seat_count > 0:
                    db_session.rollback()
                    db_session.execute('UNLOCK TABLES;')
                    return False, \
                        'Ce siège est déjà occupé ou réservé !'

            # Book ticket for 10 minutes
            reserved_until = datetime.now() + timedelta(minutes=10)

            # Insert ticket
            ticket = Ticket(ticket_type, user_id, price,
                            reserved_until=reserved_until, seat_num=seat_num)
            db_session.add(ticket)

            db_session.commit()
            db_session.execute('UNLOCK TABLES;')
            return True, ticket
        except Exception as e:
            db_session.rollback()
            db_session.execute('UNLOCK TABLES;')
            print(str(e))
            return False, '''\
Une erreur inconnue être survenue lors de la réservation de votre bilet.'''


class Payment():
    query = db_session.query_property()

    def __init__(self, amount, ticket_id, paypal_payment_id):
        self.amount = amount
        self.ticket_id = ticket_id
        self.paypal_payment_id = paypal_payment_id

    def __repr__(self):
        return '<Seat %r>' % (self.id)


class Team():
    query = db_session.query_property()

    def __init__(self, name, game, captain_id):
            self.name = name
            self.game = game
            self.captain_id = captain_id
            self.created_date = datetime.now

    def __repr__(self):
            return '<Team %r>' % (self.name)

    def get_team_id(self):
        return Team.query.filter(Team.name == self.name) \
            .filter(Team.game == self.game).first().id

    def get_captain_name(self):
        user = User.query.filter(User.id == self.captain_id).first()
        if user:
            return user.username

    def as_pub_dict(self):
            pub_dict = {
                'id': self.get_team_id(),
                'name': self.name,
                'game': self.game,
                'captain_name': self.get_captain_name(),
                }
            return pub_dict


class TeamUser():
    query = db_session.query_property()

    def __init__(self, team_id, user_id, accepted=False):
            self.team_id = team_id
            self.user_id = user_id
            self.accepted = accepted

    def __repr__(self):
            return '<Team-User %r - %r>' % (self.team_id, self.user_id)

    def get_team_name(self):
        team = User.query.filter(Team.id == self.team_id).first()
        if team:
            return team.name

    def get_user_name(self):
        user = User.query.filter(User.id == self.user_id).first()
        if user:
            return user.username

    def as_pub_dict(self):
            pub_dict = {
                'username': self.get_user_name,
                'team_name': self.get_team_name,
                'accepted': self.accepted
                }
            return pub_dict

teams = Table('teams', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(255), nullable=False),
              Column('game', String(255), nullable=False),
              Column('captain_id', Integer, ForeignKey('users.id')),
              Column('created_at', DateTime, default=datetime.now),
              Column('modified_at', DateTime, onupdate=datetime.now)
              )

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('username', String(255), nullable=False),
              Column('firstname', String(255), nullable=False),
              Column('lastname', String(255), nullable=False),
              Column('email', String(255), nullable=False),
              Column('phone', String(255), nullable=False),
              Column('created_at', DateTime, default=datetime.now),
              # private fields
              Column('modified_at', DateTime, onupdate=datetime.now),
              Column('password', Binary(64), nullable=False),
              Column('salt', String(32), nullable=False),
              Column('confirmed', Boolean, default=False),
              Column('confirmation_token', String(32))
              )

team_users = Table('team_users', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('team_id', Integer, ForeignKey('teams.id')),
                   Column('user_id', Integer, ForeignKey('users.id')),
                   Column('accepted', Boolean, nullable=False)
                   )

tickets = Table('tickets', metadata,
                Column('id', Integer, primary_key=True),
                # pc or console
                Column('type_id', Integer, nullable=False),
                # avoid n-n for now...
                Column('owner_id', Integer, ForeignKey('users.id'),
                       nullable=False),
                Column('seat_num', Integer),
                # Look for related payment and remove this field ?
                Column('paid', Boolean, default=False, nullable=False),
                Column('price', Float, nullable=False),
                Column('discount_amount', Float, default=0, nullable=False),
                Column('total', Float, default=0, nullable=False),
                Column('reserved_until', DateTime, nullable=False),
                # private fields
                Column('qr_token', String(32), nullable=False),
                Column('created_at', DateTime, default=datetime.now),
                Column('modified_at', DateTime, onupdate=datetime.now)
                )

payments = Table('payments', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('ticket_id', Integer, ForeignKey('tickets.id')),  # SKU
                 Column('paypal_payer_id', String(255)),  # nullable
                 Column('paypal_payment_id', String(255), nullable=False),
                 Column('amount', Float, nullable=False),
                 Column('created_at', DateTime, default=datetime.now),
                 Column('modified_at', DateTime, onupdate=datetime.now)
                 )

mapper(User, users)
mapper(Ticket, tickets, properties={
    'owner': relationship(User)
})
mapper(Team, teams)
mapper(TeamUser, team_users)
mapper(Payment, payments)
