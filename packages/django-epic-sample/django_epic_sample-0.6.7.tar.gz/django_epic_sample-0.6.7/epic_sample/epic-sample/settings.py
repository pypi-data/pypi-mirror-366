"""
Django settings for epic-sample project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')rg1j00sq*po(cfq^868ptyj(sb9jo3m!ac5z0p21x)&%ccb&q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

django_dir = os.path.dirname(__file__)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join (django_dir, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        }
    },
]

STATICFILES_DIRS = (
    os.path.join (django_dir, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_filters',
    'dal',		# django-autocomplete-light
    'dal_select2',
    'crispy_forms',
    'crispy_bootstrap3',
    'bootstrap3_datetime',
    'epic',
    'rest_framework'
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'epic-sample.urls'

WSGI_APPLICATION = 'epic-sample.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap3'
CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGIN_URL = '/admin/login/'
LOGOUT_URL = '/admin/logout/'

MEDIA_URL = '/media/'

# Where to store cached data.  For development, we use the local
# memory cache.  For production, you'd want to use a real cache such
# as Memcached or Redis.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    },
    'epic': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'OPTIONS': {
            'MAX_ENTIRIES': 10000
        }
    }
}

# EPIC config:
# Used in export.py to include the 'Bill To' address for orders.
EPIC_BILL_TO_ADDRESS =	'MyCompany Inc.\n' \
                        '1234 Street Blvd.\n' \
                        'Spaceport City, NM 87654'
EPIC_SHIPPING_TYPE =	'FedEx Ground'	# default/preferred ship-type
EPIC_SHIPPING_ACCOUNT =	'123456789'

# When using the make-bom script to create a BOM (assembly) from a
# Kicad schematic, the part created to represent the BOM has the
# manufacturer name set to this string.
EPIC_MANUFACTURER =	'MyCompany'

# The name of the directory under MEDIA_ROOT that contains datasheets.
# This defaults to 'epic/datasheets'
#EPIC_DATASHEET_DIR =	'epic/datasheets'

# Max. size of a datasheet in bytes:
#EPIC_DATASHEET_MAX_SIZE = (20*1024*1024)

# Directory containing KiCad-style footprints (.kicad_mod files):
EPIC_KICAD_FOOTPRINTS_DIR =	'/usr/local/lib/kicad-lib/footprints/'
