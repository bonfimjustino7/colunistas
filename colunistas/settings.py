"""
Django settings for colunistas project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lb)gvnos2w+y0ii)l7-sn2v6(ky-q4a+0cv-9n1*e%-bwh5l5z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition
SITE_NAME = 'Premio Colunistas'

INSTALLED_APPS = [
    'admin_tools',
    'admin_tools.dashboard',
    'poweradmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'localflavor',
    'tabbed_admin',
    'captcha',
    'ckeditor',
    'mptt',
    'smart_selects',
    'easy_thumbnails',
    'util',
    'base',
    'inscricao',
]

# Install theme
themedir = os.path.join(BASE_DIR, '../theme')
if os.path.isdir(themedir):
    INSTALLED_APPS.insert(0, 'theme')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'cms.middleware.URLMigrateFallbackMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'colunistas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'admin_tools.template_loaders.Loader',
            ]
        },
    },
]

WSGI_APPLICATION = 'colunistas.wsgi.application'

TABBED_ADMIN_USE_JQUERY_UI = True

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
]

LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Decimal format
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'
USE_THOUSAND_SEPARATOR = True

DATE_INPUT_FORMATS = ('%d/%m/%Y',)
SHORT_DATE_FORMAT = 'd/m/Y'
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
SHORT_DATETIME_FORMAT = 'd/m/Y, H:i:s'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

STATIC_URL = '/static/'
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
ADMIN_MEDIA_ROOT = os.path.join(STATIC_ROOT, 'admin')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# django-admin-tools
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')
CKEDITOR_UPLOAD_PREFIX = MEDIA_URL + 'uploads/'
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            {
                'name': 'document',
                'items': [
                    'Source', '-', 'Preview'
                ]
            },
            {
                'name': 'basicstyles',
                'groups': [
                    'basicstyles', 'cleanup'
                ],
                'items': [
                    'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'
                ]
            },
            {'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align'],
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            '/',
            {
                'name': 'styles',
                'items': [
                    'Styles', 'Format'
                ]
            },
            {
                'name': 'colors',
                'items': [
                    'TextColor', 'BGColor'
                ]
            },
            {
                'name': 'tools',
                'items': [
                    'Maximize', 'ShowBlocks'
                ]
            },
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule']},
        ],
        'contentsCss': [
            os.path.join(STATIC_URL, 'ckeditor_config/content.css'),
        ],
        'stylesSet': 'my_styles:%s' % os.path.join(STATIC_URL, 'site/js/ckeditor_styles.js'),
        'allowedContent': True,
    },
}

LOGIN_URL = '/login/'
