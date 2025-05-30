import os

# Unique identifiers
PROJECT_UID = os.getenv('PROJECT_UID')
VERSION_UID = os.getenv('VERSION_UID')
FORM_UUID = os.getenv('FORM_UUID')
ENKETO_FORM_UID = os.getenv('ENKETO_FORM_UID', '')

# Auth
API_TOKEN = os.getenv('API_TOKEN', '')
DIGEST_USER = os.getenv('DIGEST_USER')
DIGEST_PASS = os.getenv('DIGEST_PASS')

# URLs
ENKETO_SUBDOMAIN = os.getenv('ENKETO_SUBDOMAIN', 'ee')
KC_SUBDOMAIN = os.getenv('KC_SUBDOMAIN', 'kc')
KPI_SUBDOMAIN = os.getenv('KPI_SUBDOMAIN', 'kf')
SCHEME = os.getenv('SCHEME', 'https')
DOMAIN_NAME = os.getenv('DOMAIN_NAME', 'kobotoolbox.org')

# Misc
ASSETS_DIR = 'assets/'
