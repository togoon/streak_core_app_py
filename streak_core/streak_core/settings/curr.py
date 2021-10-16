from .base import *
import os

INSTALLED_APPS += (
        
    )

import mongoengine

DEBUG = False #True
ALLOWED_HOSTS = ['streak.tech','streak.zerodha.com','127.0.0.1','0.0.0.0','www.streak.tech','elb.streak.ninja','streak.ninja','api.streak.ninja','api.streak.tech']
DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'screener_cache': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'screener_plan': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 3600*12
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ENV = 'dev'

AUTOCOMPLTE_SECRET = 'palantir'

STATIC_ROOT = '/home/ubuntu/static/'
# mongo_password = ''
MONGO_PASSWORD = 'syFUm,~t(SXCtBckYH2s8vNbg@7#ysUc.kL3paAFaSj^LM'
MONGO_DB_ADDRESS = 'mdb.streak.tech'
MONGO_URL = 'mongodb://mongoDB-core-app-dev:' + MONGO_PASSWORD + '@'+MONGO_DB_ADDRESS+':27017/test'
mongoengine.connect('test', host=MONGO_URL,connect=False)

KITE_API_KEY = "g0sjffygw9m77dnq"
KITE_API_SECRET = "a1dz1f2lrqqu432cxbkpzurvy5uubl73"
KITE_HEADER = True


BT_URL1 = 'https://bt.streak.ninja/backtest_service'
BT_URL2 = 'https://bt.streak.ninja/backtest_service'

configs = None

RECAPTCHA_SECRET = "6Lfx5okaAAAAAGQEaYgJTcPjxPj_7fuZZLsBR0-p"

try: 
    with open(os.environ.get('STREAK_CONFIG')) as f:
        configs = json.loads(f.read())
except:
    print 'Set the environment variable STREAK_CONFIG'
    with open('../streak_core_app_config.json') as f:
        configs = json.loads(f.read())
