# production configuration

from lanmomo.settings.base import *
import lanmomo.settings.env as env

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lanmomo',
        'USER': env.DB_USER,
        'PASSWORD': env.DB_PASS,
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
