"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modcore.log import LogSupport


logger = LogSupport()
logger.logname = "http"


HTTP_CRLF = "\r\n"


class HTTPRequestException(Exception):
    pass


class ConnectionClosedException(HTTPRequestException):
    pass


class BadRequestException(HTTPRequestException):
    pass


class NotAllowedException(HTTPRequestException):
    pass


class InternalErrorException(HTTPRequestException):
    pass


class HTTPRequest:
    def __init__(self, client_addr, method, path, proto, header, body=None):
        self.client_addr = client_addr
        self.method = method.upper()
        self.path = path
        self.proto = proto
        self.header = header
        self.body = body
        self.overflow = False

    def __repr__(self):
        return (
            self.__class__.__name__
            + " "
            + str(self.client_addr[0])
            + " "
            + self.method
            + " "
            + self.path
            + " "
            + self.proto
            + " "
            + repr(self.header)
            + " "
            + (
                "<overflow>"
                if self.overflow
                else (str(len(self.body)) if self.body != None else "<empty>")
            )
        )

    def ok(self):
        return not self.overflow

    def content_len(self):
        contlen = self.header.get("Content-Length".upper(), None)
        if contlen != None:
            return int(contlen)

    def get_mime(self):
        mime = self.header.get("Content-Type".upper(), None)
        return mime.lower() if mime != None else mime


def parse_header(line):
    pos = line.index(":")
    if pos < 0:
        return line.strip(), None
    return line[0:pos].strip(), line[pos + 1 :].strip()


def get_http_read(client_file, toread, tout=None):
    return client_file.read(toread)


def get_http_readline(client_file, tout=None):
    return client_file.readline()


def get_http_request(client_file, client_addr, allowed=None, tout=None):

    if allowed == None:
        allowed = ALLOWED_DEFAULT

    line = get_http_readline(client_file, tout=tout)

    if len(line) == 0:
        raise ConnectionClosedException()

    try:
        method, path, proto = line.decode().strip().split(" ")
    except:
        raise BadRequestException(line)

    method = method.upper()
    if method not in allowed:
        raise NotAllowedException(line)

    if path[0] != "/":
        raise BadRequestException(line)

    request_header = {}
    last_header = None
    while True:
        line = get_http_readline(client_file, tout=tout)
        if not line or line == b"\r\n":
            break
        # support for multiple line spawning/ folding headers
        # with leading space, or tab
        if line[0] in [" ", "\t"]:
            logger.warn("## untested header parsing")
            request_header[last_header] += line.decode()
            logger.warn("## untested header parsing")
            continue
        header, value = parse_header(line.decode())
        last_header = header.upper()
        # no support for multi headers
        request_header[last_header] = value

    return HTTPRequest(client_addr, method, path, proto, request_header)


def get_http_content(client_file, req, max_size=4096, tout=None):
    toread = req.content_len()
    if toread != None:
        logger.info("toread", str(toread))
        if toread < max_size:
            content = get_http_read(client_file, toread, tout=tout)
            req.body = content
        else:
            req.overflow = True
    return req


def get_http_chunk(client_file, req, chunk_size=256, tout=None):
    content = get_http_read(client_file, toread=chunk_size, tout=tout)
    return content


def send_http_sequence(client_file, seq):
    for s in seq:
        if s != None:
            client_file.send(str(s))


def send_http_status(client_file, st=200, ststr=None):
    send_http_sequence(client_file, ["HTTP/1.0 ", st, ststr, HTTP_CRLF])


def send_http_header(client_file, header, value, sep=": "):
    send_http_sequence(client_file, [header, sep, value, HTTP_CRLF])


def send_http_data(client_file, data=None, data_i=None, data_len=None):
    if data_len != None:
        send_http_header(client_file, "Content-Length", data_len)
    client_file.send(HTTP_CRLF)
    if data != None and len(data) > 0:
        client_file.send(data)
    if data_i != None:
        for chunk in data_i():
            if chunk == None:
                continue
            if len(chunk) == 0:
                continue
            client_file.send(chunk)


def send_http_data_g(client_file, data=None, data_i=None, data_len=None):
    if data_len != None:
        send_http_header(client_file, "Content-Length", data_len)
        yield
    client_file.send(HTTP_CRLF)
    yield
    if data != None and len(data) > 0:
        client_file.send(data)
        yield
    if data_i != None:
        for chunk in data_i():
            yield
            if chunk == None:
                continue
            if len(chunk) == 0:
                continue
            client_file.send(chunk)


def send_http_response_header(client_file, status=200, header=None, type="text/html"):
    send_http_status(client_file, status)
    if header != None:
        for h, v in header:
            # print("header",h,v)
            send_http_header(client_file, h, v)
    if type != None:
        send_http_header(client_file, "Content-Type", type)


def send_http_response_header_g(client_file, status=200, header=None, type="text/html"):
    send_http_status(client_file, status)
    yield
    if header != None:
        for h, v in header:
            # print("header",h,v)
            send_http_header(client_file, h, v)
            yield
    if type != None:
        send_http_header(client_file, "Content-Type", type)
        yield


def send_http_response(
    client_file,
    status=200,
    header=None,
    response=None,
    type="text/html",
    response_i=None,
):
    send_http_response_header(client_file, status, header, type)

    data_len = None
    if response != None:
        if response_i == None:
            data_len = len(response)

    return send_http_data(
        client_file, data=response, data_i=response_i, data_len=data_len
    )


def send_http_response_g(
    client_file,
    status=200,
    header=None,
    response=None,
    type="text/html",
    response_i=None,
):

    yield from send_http_response_header_g(client_file, status, header, type)

    data_len = None
    if response != None:
        if response_i == None:
            data_len = len(response)

    yield from send_http_data_g(
        client_file, data=response, data_i=response_i, data_len=data_len
    )
