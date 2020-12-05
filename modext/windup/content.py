"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import os

from modcore.log import LogSupport
from modext.http.webserv import RequestHandler
from modext.http.http_func import BadRequestException
from .mime import get_file_content_type_header


class ContentGenerator(LogSupport):
    def __init__(self, root=None, suppress_id=False):
        LogSupport.__init__(self)
        self.suppress_id = suppress_id
        self.root = root if root != None else ""
        self.xroot = self.root + "/"
        self.xlen = len(self.root)
        self.info("serving", self.xroot)

    def _root_match(self, path):
        if self.xlen > 0:
            return path.startswith(self.xroot)
        # continue
        return None

    def handle(self, request):
        pass


class StaticFiles(ContentGenerator):
    def __init__(self, static_paths, root=None, send_buffer=512, fibered=True):
        ContentGenerator.__init__(self, root)
        self.static_paths = static_paths
        self.send_buffer = send_buffer
        self.fibered = fibered

    def handle(self, req):

        if self.static_paths == None or len(self.static_paths) == 0:
            return

        request = req.request
        path = request.xpath

        rc = self._root_match(path)
        if rc != None:
            if rc == False:
                return
            path = path[self.xlen :]

        if path[0] != "/":
            raise BadRequestException("malformed path", path)

        if path.find("..") >= 0:
            ## todo
            raise BadRequestException("relative path", path)

        if not self._handle_index(req, path):
            return self._handle_file(req, path)
        return True

    def _handle_index(self, req, path):
        """
        url schema is different:
        - your-ip/url
        - your-ip/url/

        important:
        only with a trailing '/' the index file handling is done
        """
        if path.endswith("/"):
            path += "index"
        if path.endswith("/index"):
            for p in [".html", ".htm"]:
                fp = path + p
                if self._handle_file(req, fp):
                    return True

    ## todo fiber, and fiber stream
    def _handle_file(self, req, path):
        for p in self.static_paths:
            fp = p + path
            try:
                ## todo checking valid path
                self.info("check root", self.root, "path", fp)
                if StaticFiles.is_file(fp):
                    self.info("found", fp)
                    self.send_file(req, fp)
                    self.info("send", fp)
                    return True
            except Exception as ex:
                self.excep(ex)

    @staticmethod
    def is_file(fnam):
        try:
            stat = os.stat(fnam)
            return stat[0] == 0x8000
        except Exception as ex:
            pass
            # self.excep( ex )
        return False

    @staticmethod
    def file_len(fnam):
        try:
            stat = os.stat(fnam)
            if stat[0] != 0x8000:
                return
            return stat[6]
        except Exception as ex:
            pass

    def send_file(self, request, path):
        header = None
        try:
            cont_type = get_file_content_type_header(path)
            if cont_type:
                header = header or []
                header.append(cont_type)
        except Exception as ex:
            self.excep(ex, "send file")
        return StaticFiles._send_chunked_file(
            request,
            path,
            send_buffer=self.send_buffer,
            fibered=self.fibered,
            log_base=self,
            header=header,
        )

    # class static scope
    def _send_chunked_file(
        request, path, send_buffer=512, fibered=True, log_base=None, header=None
    ):
        def _send_chunk():
            with open(path) as f:
                while True:
                    c = f.read(send_buffer)
                    if log_base != None:
                        log_base.info("send bytes", len(c))
                    if len(c) == 0:
                        break
                    yield c

        file_len = StaticFiles.file_len(path)

        request.send_response(
            response_i=_send_chunk,
            fibered=fibered,
            header=header,
            type_=None,
            length=file_len,
        )
