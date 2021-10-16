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
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD":"",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default" 
SESSION_COOKIE_AGE = 3600*10
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ENV = 'dev'

AUTOCOMPLTE_SECRET = 'testing'
# mongo_password = ''
# MONGO_URL = 'mongodb://localhost:27017/test'
MONGO_URL = 'mongodb://localhost:27017/test'
mongoengine.connect('test', host=MONGO_URL,connect=False)
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

BT_URL1 = 'http://localhost:5000/backtest_service'
BT_URL2 = 'http://localhost:5000/backtest_service'

KITE_API_KEY = "bi3hv3u8bj3k2gg9"
KITE_API_SECRET = "3qwzxolsh92dfwzrpa1i3v3urw6shbem"
KITE_HEADER = True

