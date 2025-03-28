import os
from os.path import join
from datetime import timedelta
# flake8: noqa
from keycloak_oidc.default_settings import *
from .azure_settings import Azure

from opencensus.trace import config_integration
from azure.identity import WorkloadIdentityCredential
from opencensus.ext.azure.trace_exporter import AzureExporter

azure = Azure()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'
config_integration.trace_integrations(['requests', 'logging', 'postgresql'])

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',            # utilities for rest apis
    'rest_framework.authtoken',  # TODO: remove once all user management is done using Grip
    'django_filters',            # for filtering rest endpoints
    'constance',
    'constance.backends.database',  # for dynamic configurations in admin
    'mozilla_django_oidc',       # for authentication
    'webpack_loader',
    'multiselectfield',
    'keycloak_oidc',
    'corsheaders',
    'captcha',                  # captcha for feedback form
    'web.core',
    'web.documents',
    'web.timeline',
    'web.users',
    'web.organizations',
    'web.roles',
    'web.cases',
    'web.profiles',
    'web.forms',
    'web.feedback',
    'web.alerts',

)
SOURCE_COMMIT = os.environ.get('COMMIT_HASH')
BRANCH_NAME = os.environ.get('BRANCH_NAME')

# https://docs.djangoproject.com/en/2.0/topics/http/middleware/
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'web.users.middleware.SessionRefresh',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'opencensus.ext.django.middleware.OpencensusMiddleware',
)

ROOT_URLCONF = os.environ.get('DJANGO_ROOT_URLCONF', 'web.urls')

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'local')
WSGI_APPLICATION = 'wsgi.application'

# Email SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'prd.mail-relay.secumailer.cloud'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
FROM_EMAIL = 'no-reply@amsterdam.nl'


ADMINS = (
    ('admin', 'name@email.com'),
)

AUTH_USER_MODEL = 'users.User'


# Database
DATABASE_HOST = os.getenv("DATABASE_HOST", "database")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dev")
DATABASE_USER = os.getenv("DATABASE_USER", "dev")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "dev")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_OPTIONS = {'sslmode': 'allow', 'connect_timeout': 5}

if 'azure.com' in DATABASE_HOST:
    DATABASE_PASSWORD = azure.auth.db_password
    DATABASE_OPTIONS['sslmode'] = 'require'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "CONN_MAX_AGE": 60 * 5,
        "PORT": DATABASE_PORT,
        'OPTIONS': {'sslmode': 'allow', 'connect_timeout': 5},
    },
}


# General
APPEND_SLASH = True
TIME_ZONE = 'Etc/GMT'
LANGUAGE_CODE = 'nl-nl'
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True
# USE_TZ = True
FRONTEND_TIMEZONE = 'Europe/Amsterdam'
DATE_FORMAT = 'd-m-Y H:i'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = os.environ.get('DJANGO_STATIC_URL', '/static/')
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'media'))

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.core.context_processors.app_settings',
                'web.alerts.context_processors.alerts_processor',
            ],
            # 'loaders': [
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]


# Password Validation
# https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    )
}

# CORS and allowed hosts
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'

SECURE_REFERRER_POLICY = "strict-origin"

AUTH_GROUPNAME_PROCESS = 'proces'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 60 * 60  # 60 minutes
LOGIN_URL = '/#login'
LOGIN_URL_NAME = 'inloggen'
LOGOUT_URL_NAME = 'uitloggen'

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/'
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ALLOW_DATA_ACCESS_KEY = 'ALLOW_DATA_ACCESS'
CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY = 'BRK_AUTHENTICATION_TOKEN'
CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY = 'BRK_AUTHENTICATION_TOKEN_EXPIRY'
CONSTANCE_HOMEPAGE_INTRO_KEY = 'HOMEPAGE_INTRO'
CONSTANCE_NEW_USER_INTRO_KEY = 'NEW_USER_INTRO'
CONSTANCE_FEEDBACK_RECIPIENT_LIST_KEY = 'FEEDBACK_RECIPIENT_LIST'
CONSTANCE_CASE_DELETE_SECONDS_KEY = 'CASE_DELETE_SECONDS'

CONSTANCE_CONFIG = {
    CONSTANCE_ALLOW_DATA_ACCESS_KEY: (True, 'Allow data to be accesible through the API'),
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_KEY: ('', 'Authentication token for accessing BRK API'),
    CONSTANCE_BRK_AUTHENTICATION_TOKEN_EXPIRY_KEY: ('', 'Expiry date for BRK API token'),
    CONSTANCE_HOMEPAGE_INTRO_KEY: ('', 'Homepage introduction html'),
    CONSTANCE_NEW_USER_INTRO_KEY: ('', 'Nieuwe gebruiker introduction html'),
    CONSTANCE_FEEDBACK_RECIPIENT_LIST_KEY: ('', 'Feedback ontvangers lijst(kommagescheiden)'),
    CONSTANCE_CASE_DELETE_SECONDS_KEY: (60 * 60 * 24 * 30, 'Na het aantal seconden nadat de persoonlijk begeleider de cliënt het verzoek om de cliënt te verwijderen heeft ingediend, wordt de cliënt echt verwijderd. Standaard is dit 30 dagen (60*60*24*30)'),
}

OIDC_RP_CLIENT_ID = os.environ.get('IAM_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('IAM_CLIENT_SECRET')

OIDC_FEDERATION_KEY = os.environ.get('OIDC_FEDERATION_KEY', 'federation')
OIDC_FEDERATION_DEFAULT = 'onbekend'

IAM_URL = None
if os.environ.get("IAM_URL"):
    IAM_URL = '%s%s' % (
        os.environ.get(
            'IAM_URL', 'https://iam.amsterdam.nl/auth/realms/datapunt-acc'
        ),
        '/protocol/openid-connect/'
    )
    OIDC_OP_AUTHORIZATION_ENDPOINT = '%s%s' % (IAM_URL, 'auth')
    OIDC_OP_TOKEN_ENDPOINT = '%s%s' % (IAM_URL, 'token')
    OIDC_OP_USER_ENDPOINT = '%s%s' % (IAM_URL, 'userinfo')
    OIDC_OP_JWKS_ENDPOINT = '%s%s' % (IAM_URL, 'certs')
    OIDC_OP_LOGOUT_ENDPOINT = '%s%s' % (IAM_URL, 'logout')
    # OIDC_AUTHENTICATION_CALLBACK_URL = 'inloggen'
    OIDC_AUTHENTICATE_CLASS = 'web.users.views.OIDCAuthenticationRequestView'
    OIDC_RP_SCOPES = 'profile email openid'
    OIDC_USE_NONCE = False
    AUTHENTICATION_BACKENDS = [
        'web.users.auth.OIDCAuthenticationBackend',
    ]

    #TODO Can probably be removed because it is defined twice, needs to be tested
    MIDDLEWARE = (
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'web.users.middleware.SessionRefresh',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'opencensus.ext.django.middleware.OpencensusMiddleware',
    )
    LOGIN_URL_NAME = 'oidc_authentication_callback'
    LOGOUT_URL_NAME = 'oidc_logout'
    LOGIN_URL = '/oidc/authenticate/'


LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "WARNING")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": LOGGING_LEVEL},
        "celery": {
            "level": LOGGING_LEVEL,
            "class": "logging.StreamHandler"
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOGGING_LEVEL
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "": {
            "level": LOGGING_LEVEL,
            "handlers": ["console"],
            "propagate": True,
        }
    },
}

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    # Only log queries when in DEBUG due to high cost
    def filter_traces(envelope):
        if LOGGING_LEVEL == "DEBUG":
            return True
        log_data = envelope.data.baseData
        if 'query' in log_data["name"].lower():
            return False
        if log_data["name"] == "GET /":
            return False
        return True
    exporter = AzureExporter(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING)
    exporter.add_telemetry_processor(filter_traces)
    OPENCENSUS = {
        "TRACE": {
            "SAMPLER": "opencensus.trace.samplers.ProbabilitySampler(rate=1)",
            "EXPORTER": exporter,
        }
    }
    LOGGING["handlers"]["azure"] = {
        "level": LOGGING_LEVEL,
        "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
        "connection_string": APPLICATIONINSIGHTS_CONNECTION_STRING,
    }
    LOGGING["root"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"]["django"]["handlers"] = ["azure", "console"]
    LOGGING["loggers"][""]["handlers"] = ["azure", "console"]

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=4),
    # We don't refresh tokens yet, so we set refresh lifetime to zero
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=0),
}

ACCESS_LOG_EXEMPTIONS = (
    '/state/health',
)

# BRK Access request settings
BRK_ACCESS_CLIENT_ID = os.getenv('BRK_ACCESS_CLIENT_ID')
BRK_ACCESS_CLIENT_SECRET = os.getenv('BRK_ACCESS_CLIENT_SECRET')
BRK_ACCESS_URL = os.getenv('BRK_ACCESS_URL')
BRK_API_OBJECT_EXPAND_URL = 'https://acc.api.data.amsterdam.nl/brk/object-expand/'

BAG_API_SEARCH_URL = 'https://api.data.amsterdam.nl/atlas/search/adres/'

AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")

if AZURE_CONTAINER:
    AZURE_TOKEN_CREDENTIAL = WorkloadIdentityCredential()
    # DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "token_credential": WorkloadIdentityCredential(),
                "account_name": os.getenv("AZURE_ACCOUNT_NAME"),
                "azure_container": AZURE_CONTAINER,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


ALLOWED_FILE_EXTENSIONS = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".xlsx", ".xls", ".doc"]
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]
