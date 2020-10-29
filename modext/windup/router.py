"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from .content import ContentGenerator, LogSupport
from .regex import xurl_params


class Router(ContentGenerator):
    def __init__(self, root=None):
        ContentGenerator.__init__(self, root)
        self.route = []

    def handle(self, req):

        req.request.xurl = None

        self.debug("searching route")
        request = req.request

        for to, method, func, xtract in self.route:

            rc = self._root_match(request.xpath)
            if rc != None:
                if rc == False:
                    return

            path = request.xpath[self.xlen :]
            cond = to == path

            if xtract:
                xurl = xurl_params(to, path)
                if xurl == None:
                    continue
                cond = True

            # url = self.root + to

            if cond and (method == None or method == request.method):
                self.info("found route", self.root, to, method, func)

                args = request.xargs
                if xtract:
                    args.set_attr("rest", xurl)

                f = func(req, args)
                return True

    def _append(self, to, method, func, xtract):
        if method != None:
            method = method.upper()
        self.route.append((to, method, func, xtract))

    def _decor(self, to, method, xtract=False):
        self.info("route", self.root + to, "for", "all" if method == None else method)
        if to[0] != "/":
            raise Exception("malformed route", to)

        def dector(f):
            # @functools.wraps(f)
            def inner(*argv, **kwargs):
                self.info("call route ", self.root, to)
                res = f(*argv, **kwargs)
                return res

            self._append(to, method, inner, xtract)
            return inner

        return dector

    def get(self, to):
        return self._decor(to, "GET")

    def post(self, to):
        return self._decor(to, "POST")

    def xget(self, to):
        return self._decor(to, "GET", True)

    def xpost(self, to):
        return self._decor(to, "POST", True)

    def __call__(self, to="/index", method=None, xtract=False):
        return self._decor(to, method, xtract)

    def supported_methods(self):
        allowed = set()
        for r in self.route:
            meth = r[1] if r[1] != None else "*"
            allowed.add(meth)
        return list(allowed)
