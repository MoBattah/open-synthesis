"""
Django settings for openintel project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

# http://bruno.im/2013/may/18/django-stop-writing-settings-files/

import os
import logging
import sys

from django.utils.translation import ugettext_lazy as _
import dj_database_url
import environ


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _detect_command(cmd):
    """Return True iff the user is running the specified Django admin command."""
    # https://stackoverflow.com/questions/4088253/django-how-to-detect-test-environment
    return len(sys.argv) > 1 and sys.argv[1] == cmd

TESTING = _detect_command('test')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Set defaults and read .env file from root directory
# Defaults should be "safe" from a security perspective
# NOTE: 'env' follows naming convention from the environ documentation
env = environ.Env(  # pylint: disable=invalid-name
    DEBUG=(bool, False),
    ENABLE_CACHE=(bool, True),
    ENVIRONMENT_NAME=(str, None),
    DJANGO_LOG_LEVEL=(str, "ERROR"),
    APP_LOG_LEVEL=(str, "ERROR"),
    CERTBOT_PUBLIC_KEY=(str, None),
    CERTBOT_SECRET_KEY=(str, None),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_HTTPONLY=(bool, True),
    X_FRAME_OPTIONS=(str, "DENY"),
    ALLOWED_HOSTS=(str, "*"),
    SECURE_SSL_REDIRECT=(bool, True),
    SECURE_BROWSER_XSS_FILTER=(bool, True),
    SECURE_CONTENT_TYPE_NOSNIFF=(bool, True),
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, True),
    SECURE_HSTS_SECONDS=(int, 31536000),  # default to maximum age in seconds
    ROLLBAR_ACCESS_TOKEN=(str, None),
    ROLLBAR_ENABLED=(bool, False),
    ACCOUNT_REQUIRED=(bool, False),
    ACCOUNT_EMAIL_REQUIRED=(bool, True),
    EVIDENCE_REQUIRE_SOURCE=(bool, True),
    EDIT_REMOVE_ENABLED=(bool, True),
    EDIT_AUTH_ANY=(bool, False),
    INVITE_REQUIRED=(bool, False),
    SENDGRID_USERNAME=(str, None),
    SENDGRID_PASSWORD=(str, None),
    SLUG_MAX_LENGTH=(int, 72),
    TWITTER_ACCOUNT=(str, None),
    DONATE_BITCOIN_ADDRESS=(str, None),
    INVITE_REQUEST_URL=(str, None),
    BANNER_MESSAGE=(str, None),
    PRIVACY_URL=(str, None),
    DIGEST_WEEKLY_DAY=(int, 0),  # default to Monday
    CELERY_ALWAYS_EAGER=(bool, False),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-ALLOWED_HOSTS
# NOTE: 'env' will return a value because a default is defined for 'ALLOWED_HOSTS'
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')  # pylint: disable=no-member

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django_comments',
    'webpack_loader',
    'field_history',
    'bootstrapform',
    'openach',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # notifications must appear after applications generating notifications
    'notifications',
    # invitations must appear after allauth: https://github.com/bee-keeper/django-invitations#allauth-integration
    'invitations',
]


# This is using the pre-Django 1.10 middleware API. We'll need to update once the 3rd-party libraries are updated
# to use the new API: https://docs.djangoproject.com/en/1.10/topics/http/middleware

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # LocaleMiddleware must come after SessionMiddleware and before CommonMiddleware
    # see: https://docs.djangoproject.com/en/1.10/topics/i18n/translation/#how-django-discovers-language-preference
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'field_history.middleware.FieldHistoryMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'csp.middleware.CSPMiddleware',
    # MinifyHTMLMiddleware needs to be after all middleware that may modify the HTML
    'pipeline.middleware.MinifyHTMLMiddleware',
    # Rollbar middleware needs to be last
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]

# Configure N+1 detection during DEBUG and TESTING; see https://github.com/jmcarp/nplusone
if DEBUG or TESTING:
    INSTALLED_APPS.insert(0, 'nplusone.ext.django')
    MIDDLEWARE_CLASSES.insert(0, 'nplusone.ext.django.NPlusOneMiddleware',)

NPLUSONE_RAISE = TESTING

ROOT_URLCONF = 'openintel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'openach.context_processors.site',
                'openach.context_processors.meta',
                'openach.context_processors.invite',
                'openach.context_processors.banner',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            # Template debugging is required for coverage testing
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'openintel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# https://docs.djangoproject.com/en/1.10/topics/security/#ssl-https
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
CSRF_COOKIE_HTTPONLY = env('CSRF_COOKIE_SECURE')
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SECURE_BROWSER_XSS_FILTER = env('SECURE_BROWSER_XSS_FILTER')
SECURE_CONTENT_TYPE_NOSNIFF = env('SECURE_CONTENT_TYPE_NOSNIFF')
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS')

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGES = (
    # Add new locales in LANGUAGES variable, e.g., ('az', _('Azerbaijani'))
    ('en', _('English (United States)')),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# https://docs.djangoproject.com/en/1.10/ref/contrib/sites/
SITE_ID = 1

# Update database configuration with $DATABASE_URL.
# XXX: migrate db config to use environ library?
# NOTE: 'db_from_env' follows naming convention from the Heroku documentation
db_from_env = dj_database_url.config(conn_max_age=500)  # pylint: disable=invalid-name
DATABASES['default'].update(db_from_env)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(BASE_DIR, 'assets')
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# https://github.com/owais/django-webpack-loader#default-configuration
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

# Logging configuration
# cf. https://chrxr.com/django-error-logging-configuration-heroku/
# cf. https://stackoverflow.com/questions/18920428/django-logging-on-heroku
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL'),
        },
        'openach': {
            'handlers': ['console'],
            'level': env('APP_LOG_LEVEL'),
        }
    },
}

# Email Options using sendgrid-django
if env('SENDGRID_USERNAME') and env('SENDGRID_PASSWORD'):  # pragma: no cover
    EMAIL_BACKEND = "sgbackend.SendGridBackend"
    # NOTE: django library uses _USER while Heroku uses _USERNAME
    SENDGRID_USER = env('SENDGRID_USERNAME')
    SENDGRID_PASSWORD = env('SENDGRID_PASSWORD')
else:
    logger.warning("SendGrid not configured: SENDGRID_USER, SENDGRID_PASSWORD")

# Instance configuration
SITE_NAME = env('SITE_NAME')
SITE_DOMAIN = env('SITE_DOMAIN')
ACCOUNT_REQUIRED = env('ACCOUNT_REQUIRED')
if _detect_command('createadmin'):  # pragma: no cover
    # Load the admin credentials if the admin is creating a default account (e.g., when deploying with Heroku button)
    ADMIN_USERNAME = env('ADMIN_USERNAME')
    ADMIN_PASSWORD = env('ADMIN_PASSWORD')
ADMIN_EMAIL_ADDRESS = env('ADMIN_EMAIL_ADDRESS')
PRIVACY_URL = env('PRIVACY_URL')
INVITE_REQUIRED = env('INVITE_REQUIRED')
INVITE_REQUEST_URL = env('INVITE_REQUEST_URL')
EVIDENCE_REQUIRE_SOURCE = env('EVIDENCE_REQUIRE_SOURCE')
EDIT_REMOVE_ENABLED = env('EDIT_REMOVE_ENABLED')
EDIT_AUTH_ANY = env('EDIT_AUTH_ANY')
TWITTER_ACCOUNT = env('TWITTER_ACCOUNT')
DONATE_BITCOIN_ADDRESS = env('DONATE_BITCOIN_ADDRESS')
BANNER_MESSAGE = env('BANNER_MESSAGE')
DIGEST_WEEKLY_DAY = env('DIGEST_WEEKLY_DAY')
if env('ENVIRONMENT_NAME'):
    ENVIRONMENT_NAME = env('ENVIRONMENT_NAME')
elif DEBUG:
    ENVIRONMENT_NAME = 'development'
else:
    ENVIRONMENT_NAME = 'production'

# Authentication Options:
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = env('ACCOUNT_EMAIL_REQUIRED')
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
# https://stackoverflow.com/questions/22700041/django-allauth-sends-verification-emails-from-webmasterservername
DEFAULT_FROM_EMAIL = env.get_value('DEFAULT_FROM_EMAIL', default=ADMIN_EMAIL_ADDRESS)
ACCOUNT_ADAPTER = 'openach.account_adapters.AccountAdapter'

# Invitations Options:
# https://github.com/bee-keeper/django-invitations#additional-configuration
INVITATIONS_INVITATION_ONLY = INVITE_REQUIRED
INVITATIONS_ADAPTER = ACCOUNT_ADAPTER

# Challenge/Response for Let's Encrypt. In the future, we may want to support challenge/response for multiple domains.
CERTBOT_PUBLIC_KEY = env('CERTBOT_PUBLIC_KEY')
CERTBOT_SECRET_KEY = env('CERTBOT_SECRET_KEY')

# Rollbar Error tracking: https://rollbar.com/docs/notifier/pyrollbar/#django
# Rollbar endpoint via 'endpoint' configuration is not working. For now just use the default.
ROLLBAR = {
    'enabled': env('ROLLBAR_ENABLED') and not TESTING,
    'access_token': env('ROLLBAR_ACCESS_TOKEN'),
    'environment': ENVIRONMENT_NAME,
    'root': PROJECT_ROOT,
    'branch': 'master',
}

# Content Security Policy (CSP) Header configuration
# https://django-csp.readthedocs.io/en/latest/configuration.html
# http://www.html5rocks.com/en/tutorials/security/content-security-policy/

CSP_DEFAULT_SRC = ["'self'"]

# SEO Configuration
SLUG_MAX_LENGTH = env('SLUG_MAX_LENGTH')

# django-pipeline configuration for static files
# https://django-pipeline.readthedocs.io/en/latest/configuration.html
# We're currently just using it for its HTML minification middleware
PIPELINE = {
    'PIPELINE_ENABLED': not DEBUG,
}


def _get_cache():
    if env('ENABLE_CACHE') and not TESTING:
        # https://devcenter.heroku.com/articles/django-memcache#configure-django-with-memcachier
        try:
            # NOTE: if 'MEMCACHIER_SERVERS' isn't defined, the exception will get caught as expected
            os.environ['MEMCACHE_SERVERS'] = env('MEMCACHIER_SERVERS').replace(',', ';')  # pylint: disable=no-member
            os.environ['MEMCACHE_USERNAME'] = env('MEMCACHIER_USERNAME')
            os.environ['MEMCACHE_PASSWORD'] = env('MEMCACHIER_PASSWORD')
            logger.info("Using MEMCACHIER servers: %s", env('MEMCACHIER_SERVERS'))
            return {
                'default': {
                    'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
                    'TIMEOUT': 500,
                    'BINARY': True,
                    'OPTIONS': {'tcp_nodelay': True}
                }
            }
        except:  # pylint: disable=bare-except
            # NOTE: bare except clause is OK here because all exceptions would be caused by a bad/missing configuration
            logger.warning("MEMCACHIER not configured; using local memory cache")
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
                }
            }
    else:
        # https://docs.djangoproject.com/en/1.10/topics/cache/#dummy-caching-for-development
        logger.info("ENABLE_CACHE not set; using DummyCache")
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }

# https://docs.djangoproject.com/en/1.10/topics/cache/
CACHES = _get_cache()

# http://docs.celeryproject.org/en/latest/configuration.html
# XXX: not sure why these have to be declared globally in addition to the celery app setup
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']  # set globally for safety
CELERY_RESULT_SERIALIZER = 'json'
if TESTING:
    logger.info('Enabling CELERY_ALWAYS_EAGER for testing')
    CELERY_ALWAYS_EAGER = True
else:
    CELERY_ALWAYS_EAGER = env('CELERY_ALWAYS_EAGER')

if env.get_value('CELERY_BROKER_URL', cast=str, default=None):
    CELERY_BROKER_URL = env('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
elif env.get_value('REDIS_URL', cast=str, default=None):
    logger.info('No CELERY_BROKER_URL specified, using REDIS_URL for Celery broker and result backend')
    CELERY_BROKER_URL = env('REDIS_URL')
    CELERY_RESULT_BACKEND = env('REDIS_URL')
