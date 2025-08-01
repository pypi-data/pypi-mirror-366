import logging

from .basic_web_server import basic_web_server

logger = logging.getLogger(__name__)


def make_static_handler(files):
    static = {url: (mime_type, data) for url, mime_type, data in files}
    logger.info(f"Generated {len(static)} static files")
    assert "error" in static, "Need a document called 'error'"

    def handler(uri, environ):
        code = 200
        if uri[0] != "/" or environ["REQUEST_METHOD"] != "GET":
            key = "error"
            code = 400
        else:
            key = uri[1:]
        if key not in static:
            key = "error"
            code = 404
        mime_type, data = static[key]
        return code, {"Content-Type": mime_type}, data

    return handler


def static_file_server(address_or_port, files, **kwargs):
    if isinstance(address_or_port, int):
        address_or_port = f"0.0.0.0:{address_or_port}"
    handler = make_static_handler(files)
    basic_web_server(handler, address_or_port, **kwargs)
