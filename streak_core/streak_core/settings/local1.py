from .base import *
INSTALLED_APPS += (
        
    )

import mongoengine


DEBUG = True
ALLOWED_HOSTS = ['*']
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
SESSION_COOKIE_AGE = 3600*10
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ENV = 'dev'

AUTOCOMPLTE_SECRET = 'testing'
# mongo_password = ''
# MONGO_PASSWORD = 'kh(ff6)jd54hydjb79(j7(gf5'
# MONGO_DB_ADDRESS = 'mdb.streak.ninja'
# MONGO_URL = 'mongodb://prod:' + MONGO_PASSWORD + '@'+MONGO_DB_ADDRESS+':27017/prod'
# mongoengine.connect('prod', host=MONGO_URL,connect=False)
MONGO_PASSWORD = 'syFUm,~t(SXCtBckYH2s8vNbg#7#ysUc.kL3paAFaSj^LM'
MONGO_DB_ADDRESS = 'mdb.streak.tech'
MONGO_URL = 'mongodb://mongoDB-core-app-dev:' + MONGO_PASSWORD + '@'+MONGO_DB_ADDRESS+':27017/test'
mongoengine.connect('test', host=MONGO_URL,connect=False,maxPoolSize=1000)
# KITE_API_KEY = '2b0bx36bnep2vslf'
# KITE_API_SECRET = 'j7zqiu2dqdi5kf2anmevfz8jths7cwuu'

# RC_DB_ADDRESS = "localhost"
# rc = r.connect(RC_DB_ADDRESS, 28015).repl()
# RC = r
# try:
#     RC.db("test").table_create("live_actions").run()
#     del RC
# except:
#     pass

BT_URL1 = 'https://1pmnue9w9f.execute-api.us-east-1.amazonaws.com/dev'
BT_URL2 = 'http://localhost:5000/backtest_service'

BT_URL1 = 'http://10.10.70.155:5000/backtest_service'
BT_URL2 = 'http://10.10.70.155:5000/backtest_service'

BT_URL1 = 'https://bt.streak.ninja/backtest_service'
BT_URL2 = 'https://bt.streak.ninja/backtest_service'

KITE_API_KEY = "g0sjffygw9m77dnq"
KITE_API_SECRET = "a1dz1f2lrqqu432cxbkpzurvy5uubl73"
KITE_HEADER = True # set true to enable kite 3

