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

    def __init__(self):
        pass

    def __repr__(self):
        return '<Ticket %r>' % (self.id)

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(1000)),
    Column('email', String(1000)),
    Column('password', Binary(64)),
    Column('salt', String(42))
)

tickets = Table('tickets', metadata,
    Column('id', Integer, primary_key=True),
    Column('type_id', Integer), # pc or console
    Column('reserved_until', Date),

)

mapper(User, users)
mapper(Ticket, tickets)
