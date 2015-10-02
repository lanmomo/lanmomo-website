import uuid

from datetime import datetime, timedelta

from sqlalchemy import Table, Column, Integer, String, Binary, Boolean, \
    ForeignKey, DateTime, Float, text
from sqlalchemy.orm import mapper

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
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at
            }
        return pub_dict


class Ticket():
    query = db_session.query_property()

    def __init__(self, type_id, owner_id, price, paid=False, reserved_until=None,
                 reserved_at=None):
        self.type_id = type_id
        self.owner_id = owner_id
        self.price = price
        self.paid = paid
        self.reserved_until = reserved_until
        self.reserved_at = reserved_at

    def __repr__(self):
        return '<Ticket %r>' % (self.id)

    def as_pub_dict(self):
        pub_dict = {
            'type_id': self.type_id,
            'owner_id': self.owner_id,
            'paid': self.paid,
            'reserved_until': self.reserved_until,
            'price': self.price,
            'discount_amount': self.discount_amount,
            'total': self.total
            }
        return pub_dict

    def book_temp(user_id, ticket_type, price, tickets_max, seat=None):
        db_session.execute('LOCK TABLES tickets write;')

        # Check if user can order a ticket
        r = text('SELECT COUNT(1) FROM tickets WHERE tickets.owner_id = :id;')
        r = r.bindparams(id=user_id)

        if db_session.execute(r).scalar() > 0:
            db_session.rollback()
            db_session.execute('UNLOCK TABLES;')
            raise Exception("Vous avez déjà un billet !")

        # Check if more tickets is allowed
        r = text('SELECT COUNT(1) FROM tickets WHERE tickets.type_id = :id;')
        r = r.bindparams(id=ticket_type)

        if db_session.execute(r).scalar() >= tickets_max[ticket_type]:
            db_session.rollback()
            db_session.execute('UNLOCK TABLES;')
            raise Exception('Le maximum de billet a été réservé pour ' +
                            'le moment !')

        # Book ticket for 10 minutes
        reserved_until = datetime.now() + timedelta(minutes=10)

        # Insert ticket
        ticket = Ticket(ticket_type, user_id, price,
                        reserved_until=reserved_until)
        db_session.add(ticket)

        db_session.commit()
        db_session.execute('UNLOCK TABLES;')
        return True


class Seat():
    query = db_session.query_property()

    def __init__(self, ticket_id, reserved_until=None, reserved_at=None):
        self.ticket_id = ticket_id

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
            return user.name

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
                # Look for related payment and remove this field ?
                Column('paid', Boolean, default=False, nullable=False),
                Column('price', Float, nullable=False),
                Column('discount_amount', Float, default=0, nullable=False),
                Column('total', Float, default=0, nullable=False),
                Column('reserved_until', DateTime, nullable=False),
                # private fields
                Column('created_at', DateTime, default=datetime.now),
                Column('modified_at', DateTime, onupdate=datetime.now)
                )

seats = Table('seats', metadata,
              Column('id', Integer, primary_key=True),
              Column('ticket_id', Integer, ForeignKey('tickets.id')),
              Column('created_at', DateTime, default=datetime.now),
              Column('modified_at', DateTime, onupdate=datetime.now)
              )

mapper(User, users)
mapper(Ticket, tickets)
mapper(Seat, seats)
mapper(Team, teams)
mapper(TeamUser, team_users)
