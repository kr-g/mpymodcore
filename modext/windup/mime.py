"""
refer also to:

https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
http://www.iana.org/assignments/media-types/media-types.xhtml
"""

_know_types = [
    (".css", "text/css"),
    (".csv", "text/csv"),
    (".gif", "image/gif"),
    (".htm", "text/html; charset=UTF-8;"),
    (".html", "text/html; charset=UTF-8;"),
    (".jpeg", "image/jpeg"),
    (".jpg", "image/jpeg"),
    (".js", "text/javascript"),
    (".json", "application/json"),
    (".mjs", "text/javascript"),
    (".png", "image/png"),
    (".svg", "image/svg+xml"),
    (".ttf", "font/ttf"),
    (".txt", "text/plain"),
    (".woff", "font/woff"),
    (".woff2", "font/woff2"),
    (".xhtml", "application/xhtml+xml"),
    (".xml", "application/xml"),
]

_look_up = {}


for ext, media_type in _know_types:
    _look_up[ext] = media_type


def get_content_type(ext, default=None):
    return _look_up.get(ext.lower(), default)


def get_content_type_header(ext):
    mime = get_content_type(ext)
    if mime:
        return ("Content-Type", mime)


def get_file_content_type_header(fnam):
    pos = fnam.rfind(".")
    if pos > 0:
        ext = fnam[pos:]
        return get_content_type_header(ext)
