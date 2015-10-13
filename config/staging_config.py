DEBUG = True
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
PAYPAL_RETURN_URL = 'http://patate.lanmomo.org/pay/execute'
# TODO check cancel url
PAYPAL_CANCEL_URL = 'http://patate.lanmomo.org/pay/cancel'

# Lanmomo
TYPE_IDS = {'pc': 0, 'console': 1}
TICKETS_MAX = {TYPE_IDS['pc']: 12, TYPE_IDS['console']: 3}
PRICING = {TYPE_IDS['pc']: 20, TYPE_IDS['console']: 10}
DISCOUNT_MOMO = 5
LOG_PATH = 'lanmomo.log'
STAGING = True
