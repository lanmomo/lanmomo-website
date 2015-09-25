import datetime
import uuid

from sqlalchemy import Table, Column, Integer, String, Binary, Boolean, \
    ForeignKey, DateTime
from sqlalchemy.orm import mapper

from database import metadata, db_session


class Subscription():
    query = db_session.query_property()

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<Subscription %r>' % (self.email)


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
        self.created_date = datetime.datetime.now
        self.confirmed = False
        self.confirmation_token = uuid.uuid4().hex

    def __repr__(self):
        return '<User %r>' % (self.username)

    def from_token(token):
        if token:
            return User.query.filter(
                User.login_token == token).first().as_pub_dict()

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

    def __init__(self, type_id, owner_id, paid=False, reserved_until=None,
                 reserved_at=None):
        self.type_id = type_id
        self.owner_id = owner_id
        self.paid = paid
        self.reserved_until = reserved_until
        self.reserved_at = reserved_at

    def __repr__(self):
        return '<Ticket %r>' % (self.id)

subcriptions = Table('subcriptions', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('email', String(1000), nullable=False)
                     )


users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('username', String(255), nullable=False),
              Column('firstname', String(255), nullable=False),
              Column('lastname', String(255), nullable=False),
              Column('email', String(255), nullable=False),
              Column('phone', String(255), nullable=False),
              Column('created_at', DateTime, default=datetime.datetime.now),
              # private fields
              Column('modified_at', DateTime, onupdate=datetime.datetime.now),
              Column('password', Binary(64), nullable=False),
              Column('salt', String(32), nullable=False),
              Column('confirmed', Boolean, default=False),
              Column('confirmation_token', String(32)),
              Column('login_token', String(32))
              )

tickets = Table('tickets', metadata,
                Column('id', Integer, primary_key=True),
                # pc or console
                Column('type_id', Integer, nullable=False),
                # avoid n-n for now...
                Column('owner_id', Integer, ForeignKey("users.id"),
                       nullable=False),
                # Look for related payment and remove this field ?
                Column('paid', Boolean, default=False, nullable=False),
                Column('reserved_until', DateTime, nullable=False),
                Column('reserved_at', DateTime, nullable=False)
                )

mapper(Subscription, subcriptions)
mapper(User, users)
mapper(Ticket, tickets)
