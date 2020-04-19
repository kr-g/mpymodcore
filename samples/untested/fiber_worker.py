
"""

in process / working / concept


"""


"""
    fiber
    https://en.wikipedia.org/wiki/Fiber_(computer_science)
    
    yield
    https://en.wikipedia.org/wiki/Cooperative_multitasking
    
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from testrecorder import TestRecorder, tid


class FiberWorkerLoop(object):
    
    def __init__(self, debug=True ):
        self.debug = debug
        self.worker = []
        
    def append(self, worker ):
        self.worker.append(worker)
        
    def remove(self, worker ):
        self.worker.remove(worker)
        
    def __iter__(self):
        return self
    
    def __next__(self):
        for w in self.worker:
            try:
                next(w)
                
            except StopIteration as ex:
                self.debug and print( self.__class__.__name__, ex.__class__.__name__, tid(w), ex )
                pass

            except Exception as ex:
                self.debug and print( self.__class__.__name__, ex.__class__.__name__, tid(w), ex )
                pass
            
    def kill(self, reason="kill" ):
        for w in self.worker:
            w.kill(reason)
    
    def close(self):
        for w in self.worker:
            w.kill("close")
        

class FiberWorker(object):
    
    def __init__(self, func, workerloop=None, parent=None, debug=True, **kwargs ):
        self.func = func
        self.floop = workerloop
        self.parent = parent
        self.debug = debug
        self._run = False
        self.kwargs = kwargs
        self.reset("init")
        
    def reset(self, reason="reset" ):
        self.kill(reason)
        self.debug and print( self.__class__.__name__, "reset", reason, tid(self),)
        self.rc = None
        self.err = None
        self._inner = self.func(self)
        
    def start(self):
        self.resume("start")
        
    def resume(self,reason="resume"):
        self.debug and print( self.__class__.__name__, "resume", reason, tid(self),) 
        try:
            if self._run or self.floop==None:
                return
            self.floop.append(self)
        finally:
            self._run = True            
        
    def suspend(self,reason="suspend"):
        self.debug and print( self.__class__.__name__, "suspend", reason, tid(self),)
        try:
            if not self._run or self.floop==None:
                return
            self.floop.remove(self)
        finally:
            self._run = False            

    def spawn_fiber(self, worker):

        worker.parent=self
        worker.resume("spawn-start")

        # exactly once!
        yield
        
        if worker.err != None:
            raise worker.err
        if worker.rc != None:
            return worker.rc

        return 1234567890

    def spawn(self, func, **kwargs ):
        self.suspend("spawn")
        worker = FiberWorker( func=func, workerloop=self.floop, debug=self.debug, **kwargs )        
        return self.spawn_fiber(worker)

    def _done_revoke_parent(self,reason="worker-done"):
        self.suspend(reason)
        if self.parent!=None:
            self.parent.resume("spawn-return")        

    def __next__(self):
        try:
            self.rc = next( self._inner )
            return self.rc
        except StopIteration as ex:
            self.debug and print( self.__class__.__name__, "stop", tid(self), ex)
            self._done_revoke_parent()
            raise ex
        except Exception as ex:
            self.debug and print( self.__class__.__name__, "except", tid(self), ex)
            self.err = ex
            self._done_revoke_parent("exception")
            raise ex
    
    def __iter__(self):
        return self
        
    def kill(self, reason="kill" ):
        self.debug and print( self.__class__.__name__, "kill", reason, tid(self),)
        self.suspend(reason)
        self._inner = None
        #untested
        if self.parent!=None:
            self.parent.kill(reason)
            self.parent = None
    
    def close(self):
        self.kill("close")
 
    
def sample():

    with TestRecorder("fiber-worker-sample",record=False,nil=False,\
                      dest_dir = "./") as tr:

        def w1func(self):
            c = 0
            while True:
                c+=1
                if c>10:
                    break
                print("w1", c, self.kwargs, tid(self) )
                yield 
           
        def w2subfunc(self):
            c=50
            while True:
                c+=1
                if c>52:
                    break
                print("w2sub", c, tid(self) )
                yield
                
            print("w2sub done", tid(self))
            # un/comment exception to test
            raise Exception("w2sub done with error", tid(self))
            # return value in rc
            yield 153

        def w2func(self):
            
            try:
                print("spawn to w2subfunc", tid(self))
                rc = yield from self.spawn( func= w2subfunc )
                print("return from w2subfunc", rc, tid(self) )
            except Exception as ex:
                print( "excep in w2subfunc", ex, tid(self) )
            
            c = 1
            while True:
                print("w2", c, self.kwargs, tid(self))
                c+=c
                yield 


        global fl
        fl = FiberWorkerLoop()

        w1 = FiberWorker( func=w1func, workerloop=fl, a=3 )
        w2 = FiberWorker( func=w2func, workerloop=fl, a=15 )
            
        w1.start()
        w2.start()

        next(fl)
        next(fl)
        next(fl)

        w1.suspend()
        print("suspend")

        print("hop1")
        next(fl)
        print("hop2")
        next(fl)

        w1.resume()
        print("resume")

        next(fl)
        next(fl)

        w1.reset()
        w1.start()

        print("reset")

        next(fl)
        next(fl)
        next(fl)
        next(fl)


sample()

