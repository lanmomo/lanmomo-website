DEBUG = True
WEB_ROOT = 'http://localhost:5000/#'
DATABASE_URI = 'sqlite:////tmp/test.db'
SECRET_KEY = 'secret'

# Mailgun
MAILGUN_USER = 'no-reply@lanmomo.org'
MAILGUN_DOMAIN = 'lanmomo.org'
MAILGUN_KEY = 'secret'

# Paypal
PAYPAL_API_ID = ''
PAYPAL_API_SECRET = ''
PAYPAL_API_MODE = 'sandbox'

# Lanmomo
TYPE_IDS = {'pc': 0, 'console': 1}
TICKETS_MAX = {TYPE_IDS['pc']: 96, TYPE_IDS['console']: 32}
PRICING = {TYPE_IDS['pc']: 20, TYPE_IDS['console']: 10}
DISCOUNT_MOMO = 5
LOG_PATH = 'lanmomo.log'

# Server
SERVER_TOKEN = 'SECRET'
