import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'commands.apps.CommandsConfig',
    'applications.tenants.apps.TenantConfig',
    'applications.traccar.apps.TraccarConfig',
    'applications.insurance_companies.apps.InsuranceCompaniesConfig',
    'applications.vehicles.apps.VehiclesConfig',
    'applications.users.apps.UsersConfig',
    'applications.allowed_vehicles.apps.AllowedVehiclesConfig',
    'applications.reservation_templates.apps.ReservationTemplatesConfig',
    'applications.reservations.apps.ReservationsConfig',
    'applications.incidents.apps.IncidentsConfig',
    'applications.tickets.apps.TicketsConfig',
    'applications.reports.apps.ReportsConfig',
    'applications.diets.apps.DietsConfig',
    'applications.maintenance.apps.MaintenanceConfig',
]

THIRD_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

ROOT_URLCONF = 'fleet_management.urls'

WSGI_APPLICATION = 'fleet_management.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    # str(BASE_DIR / "static"),
    str(BASE_DIR / "media"),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# STATIC_ROOT = '/var/www/fleet_management/static/'

MEDIA_ROOT = str(BASE_DIR / 'media')

MEDIA_URL = '/media/'


SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}
