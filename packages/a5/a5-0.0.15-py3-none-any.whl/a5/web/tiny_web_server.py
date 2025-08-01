import logging
from typing import Callable, Dict, Tuple, Union

from .wsgi_server import run_wsgi_app

logger = logging.getLogger(__name__)


def tiny_web_server(port, handler: Callable[[str], Tuple[Dict, Union[bytes, str]]]):
    def app(environ, start_response):
        if environ["REQUEST_METHOD"] != "GET":
            status = "400 Bad Request"
            headers = [("Content-type", "text/plain")]
            start_response(status, headers)
            return [b"Unsupported request."]
        uri = environ["PATH_INFO"]
        headers, response = handler(uri)
        if isinstance(response, str):
            response = response.encode("utf8")
        logger.info(f"Got request for {uri}, responding with {len(response)} bytes")
        start_response("200 OK", list(headers.items()))
        return [response]

    logger.info(f"Starting tiny HTTP server on port {port}")
    run_wsgi_app(app, f"0.0.0.0:{port}", workers=1)
