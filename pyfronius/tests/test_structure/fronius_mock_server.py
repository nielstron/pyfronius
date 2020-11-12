import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from typing import Tuple, Callable

try:
    from http import HTTPStatus
except ImportError:
    # Backwards compatability
    import http.client as HTTPStatus
import posixpath
from pathlib import Path

SERVER_DIR = Path(__file__).parent or Path(".")

class FroniusServer(HTTPServer):
    def __init__(self, server_address: Tuple[str, int], RequestHandlerClass: Callable[..., BaseHTTPRequestHandler],
                 api_version: int):
        super().__init__(server_address, RequestHandlerClass)
        self.api_version = api_version


class FroniusRequestHandler(SimpleHTTPRequestHandler):

    server: FroniusServer

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        only slightly changed method of the standard library
        """
        # abandon query parameters
        # path = path.split('?',1)[0] -> Keep them for fronius as name of file
        path = path.split("#", 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith("/")
        try:
            path = urllib.parse.unquote(path, errors="surrogatepass")
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split("/")
        words = filter(None, words)
        path = os.path.join(
            str(SERVER_DIR.absolute()),
            "v{}".format(
            self.server.api_version
        ))
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += "/"
        return path

    def send_error(self, code, message=None, explain=None):
        """
        Send blnet zugang verweigert page
        :param code:
        :param message:
        :param explain:
        :return:
        """
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        self.send_header("Connection", "close")

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        body = None
        if code >= 200 and code not in (
            HTTPStatus.NO_CONTENT,
            HTTPStatus.RESET_CONTENT,
            HTTPStatus.NOT_MODIFIED,
        ):
            # HTML encode to prevent Cross Site Scripting attacks
            # (see bug #1100201)
            # Specialized error method for fronius
            with SERVER_DIR.joinpath(
                    "v{}".format(self.server.api_version)
            ).joinpath(".error.html").open("rb") as file:
                body = file.read()
            self.send_header("Content-Type", self.error_content_type)
            self.send_header("Content-Length", int(len(body)))
        self.end_headers()

        if self.command != "HEAD" and body:
            self.wfile.write(body)
