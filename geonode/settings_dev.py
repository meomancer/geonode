from geonode.settings import *

DATABASES = {
    'default': {
        'NAME': 'geonode',
        'USER': 'geonode',
        'PASSWORD': 'geonode',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': 5,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {'options': '-c search_path=groundwater,public', 'connect_timeout': 5}},
    'datastore': {
        'NAME': 'geonode_data',
        'USER': 'geonode_data',
        'PASSWORD': 'geonode',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': 5,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {'options': '-c search_path=groundwater,public', 'connect_timeout': 5}},
    'gwml2': {
        'NAME': 'groundwater',
        'USER': 'geonode',
        'PASSWORD': 'geonode',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': 5,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {'options': '-c search_path=groundwater,public', 'connect_timeout': 5}}
}
