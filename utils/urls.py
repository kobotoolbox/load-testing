from constants import (
    SCHEME,
    DOMAIN_NAME,
    ENKETO_SUBDOMAIN,
    KC_SUBDOMAIN,
    KPI_SUBDOMAIN,
)


def get_enketo_url(endpoint: str = '') -> str:
    return SCHEME + '://' + ENKETO_SUBDOMAIN + '.' + DOMAIN_NAME + endpoint


def get_kc_url(endpoint: str = '') -> str:
    return SCHEME + '://' + KC_SUBDOMAIN + '.' + DOMAIN_NAME + endpoint


def get_kpi_url(endpoint: str = '') -> str:
    return SCHEME + '://' + KPI_SUBDOMAIN + '.' + DOMAIN_NAME + endpoint
