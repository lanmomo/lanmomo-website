from sqlalchemy import Table, Column, Integer, String, Binary, Boolean
from sqlalchemy.orm import mapper

from database import metadata, db_session

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

    def __init__(self, type_id, owner_id, paid=False, reserved_until=None, reserved_at=None):
        self.type_id = type_id
        self.owner_id = owner_id
        self.paid = paid
        self.reserved_until = reserved_until
        self.reserved_at = reserved_at

    def __repr__(self):
        return '<Ticket %r>' % (self.id)

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(1000), nullable=False),
    Column('email', String(1000), nullable=False),
    Column('password', Binary(64), nullable=False),
    Column('salt', String(42), nullable=False)
)

tickets = Table('tickets', metadata,
    Column('id', Integer, primary_key=True),
    Column('type_id', Integer, nullable=False), # pc or console
    Column('owner_id', Interger, ForeignKey("user.id"), nullable=False), # avoid n-n for now...
    Column('paid', Boolean, default=False, nullable=False), # Look for related payment and remove this field ?
    Column('reserved_until', Date, nullable=False),
    Column('reserved_at', Date, default=_get_date, nullable=False)
)

mapper(User, users)
mapper(Ticket, tickets)
