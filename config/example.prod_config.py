DEBUG = False
DATABASE_URI = 'mysql+mysqlconnector://lanmomo@localhost/lanmomo'
SECRET_KEY = 'secret'

# Mailgun
MAILGUN_USER = 'no-reply@lanmomo.org'
MAILGUN_DOMAIN = 'lanmomo.org'
MAILGUN_KEY = 'secret'

TYPE_IDS = {'pc': 0, 'console': 1}
TICKETS_MAX = {TYPE_IDS['pc']: 96, TYPE_IDS['console']: 32}
PRICING = {TYPE_IDS['pc']: 20, TYPE_IDS['console']: 10}
DISCOUNT_MOMO = 5
