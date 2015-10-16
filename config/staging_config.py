DEBUG = False
WEB_ROOT = 'http://patate.lanmomo.org'
DATABASE_URI = 'mysql+mysqlconnector://lanmomo@localhost/lanmomo'
SECRET_KEY = 'secret'

# Mailgun
MAILGUN_USER = 'no-reply@lanmomo.org'
MAILGUN_DOMAIN = 'lanmomo.org'
MAILGUN_KEY = 'secret'

# Paypal
PAYPAL_API_ID = 'get_rect()'
PAYPAL_API_SECRET = 'get_rect()'
PAYPAL_API_MODE = 'sandbox'

# Lanmomo
TYPE_IDS = {'pc': 0, 'console': 1}
TICKETS_MAX = {TYPE_IDS['pc']: 12, TYPE_IDS['console']: 3}
PRICING = {TYPE_IDS['pc']: 20, TYPE_IDS['console']: 10}
DISCOUNT_MOMO = 5
LOG_PATH = '/var/log/lanmomo/lanmomo.log'
STAGING = True
