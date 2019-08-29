import os

# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# If this file is changed in development, the development server will
# have to be manually restarted because changes will not be noticed
# immediately.

# NOTE: setting debug = true to avoid pa11y-ci timeouts
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cdhweb.db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'read_default_file': '~travis/.my.cnf'
        },
    },
}

# required with django 1.11 when debug is false, even for tests
ALLOWED_HOSTS = ["*"]

# configure django-compressor to compress css & javascript
# NOTE: compression disabled because otherwise pa11y-ci times out
COMPRESS_ENABLED = False

# compress to the sitemedia folder
COMPRESS_ROOT = os.path.join(BASE_DIR, 'sitemedia')

# run a full compress before e2e/a11y tests to serve statically
COMPRESS_OFFLINE = True

