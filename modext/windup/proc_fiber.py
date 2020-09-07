
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modext.fiber import FiberLoop, Fiber

from .proc import Processor


class ProcessorFiber(Processor):
    
    def __init__(self,windup):
        Processor.__init__(self,windup)
        
    def run(self,req):
        req.fiberloop = FiberLoop()
        return super().run(req)
        
    def loop(self):
        for status_change in self.req.fiberloop:
            # do something with status_change
            # and stop after the first loop 
            break
        self.info( "exe fiberloop done" )
        #self.req_done = self.req.fiberloop.all_done()
        
    def done(self):
        return self.req.fiberloop.all_done()
        
    def kill(self,reason=None):
        self.req.fiberloop.kill_all(reason)

    def close(self):
        self.req.fiberloop.close()
        self.req.fiberloop = None
        super().close()
        
        
