DEBUG = False
DATABASE_URI = 'mysql+mysqlconnector://lanmomo@localhost/lanmomo'
SECRET_KEY = 'secret'

# Mailgun
MAILGUN_USER = 'no-reply@lanmomo.org'
MAILGUN_DOMAIN = 'lanmomo.org'
MAILGUN_KEY = 'secret'

# Paypal
PAYPAL_API_ID = ''
PAYPAL_API_SECRET = ''
PAYPAL_API_MODE = 'live'
PAYPAL_RETURN_URL = 'https://lanmomo.org/pay/execute'
# TODO check cancel url
PAYPAL_CANCEL_URL = 'https://lanmomo.org/pay/cancel'

# Lanmomo
TYPE_IDS = {'pc': 0, 'console': 1}
TICKETS_MAX = {TYPE_IDS['pc']: 96, TYPE_IDS['console']: 32}
PRICING = {TYPE_IDS['pc']: 20, TYPE_IDS['console']: 10}
DISCOUNT_MOMO = 5
LOG_PATH = '/var/log/lanmomo/lanmomo.log'
