from sqlalchemy import Table, Column, Integer, String, Binary, Boolean, ForeignKey, Date
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

    def __init__(self, username, email, password, salt):
        self.username = username
        self.email = email
        self.password = password
        self.salt = salt

    def __repr__(self):
        return '<User %r>' % (self.username)


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
              Column('username', String(1000), nullable=False),
              Column('email', String(1000), nullable=False),
              Column('password', Binary(64), nullable=False),
              Column('salt', String(42), nullable=False)
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
                Column('reserved_until', Date, nullable=False),
                Column('reserved_at', Date, nullable=False)
                )

mapper(Subscription, subcriptions)
mapper(User, users)
mapper(Ticket, tickets)
