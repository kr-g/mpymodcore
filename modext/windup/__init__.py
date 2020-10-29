from modext.http.webserv import WebServer

from .router import Router
from .content import StaticFiles
from .core import WindUp
from .proc import Namespace


HTTP_CRLF = "\r\n"

HTTP_OK = 200
HTTP_ERR = 400

HTTP_NO_CONTENT = 204

HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_REQUEST_TIMEOUT = 408
HTTP_TEAPOT = 418

HTTP_INTERNAL = 500
HTTP_INSUFFICIENT_STORAGE = 507
HTTP_AUTH_REQUIRED = 511
