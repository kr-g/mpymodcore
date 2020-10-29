"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modcore.log import LogSupport

from modext.config import Namespace


class Processor(LogSupport):
    def __init__(self, windup):
        LogSupport.__init__(self)
        self.windup = windup
        self.req = None
        self.req_done = False

    def run(self, req):

        self.req = req

        req.load_request(self.windup.allowed)

        # when logging use argument list rather then
        # concatenate strings together -> performace
        self.info("request", req.request)
        self.info("request content len", len(req))

        request = req.request
        request.xargs = Namespace()

        for f in self.windup.headerfilter:
            rc = f.filterRequest(request)

        req.load_content(max_size=4096)
        if req.overflow == True:
            # if bodydata is too big then no data is loaded automatically
            # dont run body filters automatically if max size exceeds
            # if a request contains more data the generator
            # needs to decide what to do in detail
            #
            # some req.x-fields are then not available !!!
            # because each filter sets them on its own !!!
            #
            self.warn("no auto content loading. size=", len(req))
            self.warn("not all req.x-fields area available")
        else:
            for f in self.windup.bodyfilter:
                f.filterRequest(request)

        self.info("xargs", request.xargs)

        # after auto cleanup with filter this can be None
        body = req.request.body
        if body != None:
            self.info("request content", body)

        self.req_done = False
        for gen in self.windup.generators:
            self.req_done = gen.handle(req)
            if self.req_done:
                break

        return self.req_done

    def _after_run_done(self, req):
        pass

    def _after_run_undone(self, req):
        self.req_done = True
        self.windup.call404(req)

    def loop(self):
        pass

    def done(self):
        return self.req_done

    def stop(self):
        pass

    def kill(self, reason=None):
        pass

    def close(self):
        if self.req != None:
            self.req.close()
            self.req = None
