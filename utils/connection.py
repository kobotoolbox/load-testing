import time
from copy import deepcopy

from requests import Response
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
    MultipartEncoderMonitor,
)

from constants import API_TOKEN, DIGEST_USER, DIGEST_PASS


def add_auth_headers(headers: dict) -> dict:
    headers['Authorization'] = f'Token {API_TOKEN}'
    return headers


def authenticate_request(
    client_request_callback,
    url: str,
    data: dict = None,
    with_digest: bool = False,
    slowness_factor: float = None,
    headers: dict = None,
) -> Response:

    multi_part = None
    if not headers:
        headers = {}

    if data:
        multi_part = _get_upload_multi_encoder(data, slowness_factor)
        headers['Content-Type'] = multi_part.content_type

    if not with_digest:
        headers = add_auth_headers(headers)

    response = client_request_callback(url, data=multi_part, headers=headers)

    if (
        with_digest
        and response.status_code == 401
        and 'digest' in response.headers.get('WWW-Authenticate', '').lower()
    ):
        if data:
            multi_part = _get_upload_multi_encoder(data, slowness_factor)
            headers['Content-Type'] = multi_part.content_type

        # FIXME try to use real digest authentication. It's block as soon as Digest is
        #   used instead of Token Auth
        response = client_request_callback(
            url,
            data=multi_part,
            headers=add_auth_headers(headers),
            # auth=HTTPDigestAuth(DIGEST_USER, DIGEST_PASS),
        )

    return response


def _get_upload_multi_encoder(data: dict, slowness_factor):
    m = MultipartEncoder(fields=deepcopy(data))
    if slowness_factor:
        m = MultipartEncoderMonitor(m, lambda _: time.sleep(slowness_factor))

    return m
