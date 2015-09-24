"""
Django settings for parlhand project.

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
SECRET_KEY = 'ok4q2mlu3emizukr&kq8ci81dt!^cm#%yn!4cuevejry*z9r2*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'site','templates')]

ALLOWED_HOSTS = []
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SITE_ID = 1

# Application definition

#PACKAGE_NAME_FILEBROWSER = "filebrowser"

INSTALLED_APPS = (
    'parlhand',
    'grappelli_feincms',
    #PACKAGE_NAME_FILEBROWSER,
    'feincms',
    'grappelli',
    'mptt',
    'feincms.module.page',
    'feincms.module.medialibrary',

    'data_interrogator',
    'django_spaghetti',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    #'django.contrib.gis',
    #'django.contrib.sites',
    #'django.contrib.flatpages',
    'rest_framework',
    'reversion',
    'reversion_compare',
    'haystack',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',

    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    'django.core.context_processors.debug',
    "parlhand.context_processors.menu_handler",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'parlhand.urls'

WSGI_APPLICATION = 'parlhand.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'ENGINE': 'django.contrib.gis.db.backends.spatialite',
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
STATICFILES_DIRS = [os.path.join(BASE_DIR, "site","static")]
STATIC_ROOT=os.path.join(BASE_DIR, 'static')

MEDIA_ROOT=os.path.join(BASE_DIR, 'media')
MEDIA_URL='/media/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'parlhand-cache',
    }
}

DATA_INTERROGATION_DOSSIER = {
    'suspects': [
        {   "model":("parlhand","Person"),
            "wrap_sheets": {
                "name": {
                    "columns": ['phid','name', 'family_name'],#,'given_name'],
                    "sort" : "family_name",
                    "template": "parlhand/tables/custom/parliamentarian.html",
                },
                "length_of_service": {
                    "columns": [], # none needed this is an alias
                    "sort" : "length_of_service",
                    "template": "parlhand/tables/custom/length_of_service.html",
                }
            },
            "aliases": {
                "length_of_service":{
                        'filter':"service.chamber.level=Federal",
                        'column':"sum(service.end_date - service.start_date)",
                    },
                },
            "alias": "Parliamentian",
        },
        {'model':("parlhand","Electorate")},
        {'model':("parlhand","Ministry")},
        {'model':("parlhand","Party"),
            "wrap_sheets": {
                "code": {
                    "columns": ['code','primary_colour', 'secondary_colour'],
                    "sort" : "code",
                    "template": "parlhand/tables/custom/party_code.html",
                },
                "name": {
                    "columns": ['code','name'],
                    "sort" : "name",
                    "template": "parlhand/tables/custom/party_name.html",
                },
            },
            "alias": "Parliamentian",
        },
        {'model':("parlhand","Committee")},
        {'model':("parlhand","Service")},
    ],
    'witness_protection' : ["User","Revision","Version"],
    'suspect_grouping':True
}

SPAGHETTI_SAUCE = {
    'apps':['parlhand','popolo','popolo_behaviours'], #['tests']
    'exclude':{'parlhand':['link','identifier','othername',]},
    'show_fields':False,
    'ignore_self_referential':True,
    }
    
import os
HAYSTACK_CONNECTIONS = {
    'default': {
        #'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'ENGINE': 'parlhand.whoosh_backend.FixedWhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        'INCLUDE_SPELLING':True,
    },
}
