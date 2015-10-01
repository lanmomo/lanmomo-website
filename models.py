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
        try:
            db_session.execute('LOCK TABLES tickets WRITE;')

            # Get reservation and paid ticket total count for user
            user_ticket_count = Ticket.query \
                .filter(Ticket.owner_id == user_id) \
                .filter(Ticket.paid | Ticket.reserved_until >= datetime.now()) \
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
                .filter(Ticket.paid | Ticket.reserved_until >= datetime.now()) \
                .count()

            # Check if more tickets is allowed for this type
            if ticket_type_count >= tickets_max[ticket_type]:
                db_session.rollback()
                db_session.execute('UNLOCK TABLES;')
                return False, \
                    'Le maximum de billet a été réservé pour le moment !'

            if seat:
                # Check is seat is taken
                # TODO
                pass

            # Book ticket for 10 minutes
            reserved_until = datetime.now() + timedelta(minutes=10)

            # Insert ticket
            ticket = Ticket(ticket_type, user_id, price,
                            reserved_until=reserved_until)
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


class Seat():
    query = db_session.query_property()

    def __init__(self, ticket_id, reserved_until=None, reserved_at=None):
        self.ticket_id = ticket_id

    def __repr__(self):
        return '<Seat %r>' % (self.id)


class Payment():
    query = db_session.query_property()

    def __init__(self, amount, ticket_id, paypal_payment_id):
        self.amount = amount
        self.ticket_id = ticket_id
        self.paypal_payment_id = paypal_payment_id

    def __repr__(self):
        return '<Seat %r>' % (self.id)

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
mapper(Ticket, tickets)
mapper(Seat, seats)
mapper(Payment, payments)
