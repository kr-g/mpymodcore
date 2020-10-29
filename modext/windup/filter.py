"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import json

from modcore.log import LogSupport

from modext.http.http_func import HTTPRequestException, BadRequestException
from modext.http.webserv import COOKIE_HEADER


class FilterException(Exception):
    pass


class FilterBadRequestException(FilterException):
    pass


auto_cleanup = False


class Filter(LogSupport):
    def __init__(self, cleanup=None):
        LogSupport.__init__(self)
        if cleanup == None:
            cleanup = auto_cleanup
        self.cleanup = cleanup

    def filterRequest(self, request):
        pass


class PathSplitFilter(Filter):
    def filterRequest(self, request):
        path, query, fragment = self.split(request.path)

        request.xpath = path
        request.xquery = query
        request.xfragment = fragment

        xargs = request.xargs
        xargs["url"] = {"path": path, "query": query, "fragment": fragment}

        if self.cleanup:
            request.path = None

    def split(self, path):
        query = None
        fragment = None
        try:
            path, fragment = path.split("#")
        except:
            pass
        try:
            path, query = path.split("?")
        except:
            pass
        return path, query, fragment


class XPathSlashDenseFilter(Filter):
    def filterRequest(self, request):

        found = False
        while True:
            pos = request.xpath.find("//")
            if pos < 0:
                break

            request.xpath = request.xpath[0:pos] + request.xpath[pos + 1 :]
            request.xargs.set_attr("url.path", request.xpath)

            found = True

        #        if len(request.xpath)>1 and request.xpath[-1]=="/":
        #            request.xpath = request.xpath[0:-1]
        #            found = True

        self.info("dense", found)


class XPathDecodeFilter(Filter):
    def filterRequest(self, request):
        request.xpath = request.xpath.replace("%20", " ")
        request.xargs.set_attr("url.path", request.xpath)


class ParameterSplitFilter(Filter):
    def filterRequest(self, request):
        request.xparam = None
        if request.xquery == None:
            return
        param = self.split(request.xquery)

        request.xparam = param

        if self.cleanup:
            request.xquery = None

    def split(self, param):
        parl = param.split("&")
        parl = list(filter(lambda x: x != None and len(x) > 0, parl))
        return parl if len(parl) > 0 else None


class ParameterValueFilter(Filter):
    def filterRequest(self, request):
        request.xkeyval = None
        if request.xparam == None:
            return
        keyval = list(map(lambda x: x.split("="), request.xparam))
        request.xkeyval = keyval

        if self.cleanup:
            request.xparam = None


class ParameterPackFilter(Filter):
    def filterRequest(self, request):
        request.xpar = None
        if request.xkeyval == None:
            return
        keyval = {}
        try:
            for k, v in request.xkeyval:
                if k not in keyval:
                    keyval[k] = [v]
                    continue
                keyval[k].append(v)
        except Exception as ex:
            self.excep(ex, "invalid parameter")
        request.xpar = keyval

        if self.cleanup:
            request.xkeyval = None


class ParameterDenseFilter(Filter):
    def filterRequest(self, request):

        if request.xpar != None:

            for k, v in request.xpar.items():
                if len(v) == 1:
                    request.xpar[k] = v[0]

        request.xargs.set_attr("param", request.xpar)


class CookieFilter(Filter):
    def filterRequest(self, request):
        request.xcookies = None
        cookie = request.header.get(COOKIE_HEADER, None)
        if cookie == None:
            return
        cookies = {}
        try:
            for c in cookie.split(";"):
                c = c.strip()
                if len(c) == 0:
                    continue
                try:
                    k, v = c.split("=")
                    k = k.strip()
                except:
                    self.error("client with strange cookie", c)
                    continue
                cookies[k] = v.strip()
        except Exception as ex:
            self.excep(ex, cookie)

        request.xcookies = cookies
        request.xargs.set_attr("cookies", request.xcookies)

        if self.cleanup:
            del request.header[COOKIE_HEADER]


class BodyTextDecodeFilter(Filter):
    def __init__(self, cleanup=False, mime=None):
        Filter.__init__(self, cleanup)
        self.mime = [
            None,
            "text/plain",
            "application/x-www-form-urlencoded",
            "application/json",
            "application/ld+json",
        ]
        if mime != None:
            self.mime.extend(mime)

    def filterRequest(self, request):

        if request.body == None:
            return

        if request.get_mime() in self.mime:
            try:
                request.body = request.body.decode()
                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)


class JsonParserFilter(Filter):
    def filterRequest(self, request):

        request.xjson = None

        if request.body == None:
            return

        if request.get_mime() in ["application/json", "application/ld+json"]:
            try:

                request.xjson = json.loads(request.body)

                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)
                raise FilterBadRequestException("invalid json")

            request.xargs.set_attr("json", request.xjson)

        if self.cleanup:
            request.body = None


class FormDataFilter(Filter):
    def filterRequest(self, request):

        request.xform = None

        if request.body == None:
            return

        if request.get_mime() in ["application/x-www-form-urlencoded"]:

            request.xform = {}

            try:
                for kv in request.body.split("&"):
                    k, v = kv.split("=")
                    request.xform[k.strip()] = v.strip()

                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)

        if self.cleanup:
            request.body = None


class FormDataDecodeFilter(Filter):
    def filterRequest(self, request):

        if request.xform == None:
            request.xargs.set_attr("form", None)
            return

        if request.get_mime() in ["application/x-www-form-urlencoded"]:

            try:
                for k, v in request.xform.items():
                    val = self._conv(v)
                    request.xform[k] = val

                self.info("decoded url data", request.xform)
            except Exception as ex:
                self.excep(ex)

            request.xargs.set_attr("form", request.xform)

    def _conv(self, val):

        ## todo not fully compliant
        val = val.replace("+", " ")

        pos = 0
        while True:
            pos = val.find("%", pos)
            if pos >= 0:
                hex = val[pos + 1 : pos + 3]
                b = int(hex, 16)
                s = chr(b)
                # print(hex,b,s)
                val = val[:pos] + str(s) + val[pos + 3 :]
                pos += 1
            else:
                break
        return val
