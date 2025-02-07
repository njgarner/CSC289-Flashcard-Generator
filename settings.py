import django
from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'database_name',
        'USER': 'mysql_username',
        'PASSWORD': 'mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}