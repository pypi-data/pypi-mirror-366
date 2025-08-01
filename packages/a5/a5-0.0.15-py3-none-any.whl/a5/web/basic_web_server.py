import logging
from typing import Callable, Dict, Tuple, Union

from .http_status_codes import HTTP_STATUS_CODES
from .wsgi_server import run_wsgi_app

logger = logging.getLogger(__name__)


def basic_web_server(
    handler: Callable[[str, Dict], Tuple[Dict, Union[bytes, str]]],
    address,
    key_path=None,
    cert_path=None,
    workers=4,
):
    def app(environ, start_response):
        uri = environ["PATH_INFO"]
        logger.info(f"Got request for {uri}, calling handler")
        res = handler(uri, environ)
        if len(res) == 3:
            status, headers, response = res
        else:
            status = 200
            headers = {"Content-Type": "text/html"}
            response = res
        if isinstance(response, str):
            response = response.encode("utf8")
        if status is True:
            status = 200
        if isinstance(status, int):
            label = HTTP_STATUS_CODES.get(status, "unknown")
            status = f"{status} {label}"
        if isinstance(headers, dict):
            headers = list(headers.items())
        start_response(status, headers)
        logger.info(f"Responding to {uri}, with {status}, {len(response)} bytes, {len(headers)} headers")
        return [response]

    logger.info(f"Starting basic HTTP server on port {address}")
    run_wsgi_app(app, address, key_path=key_path, cert_path=cert_path, workers=workers)
