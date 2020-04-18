
"""

in process / working / concept


"""

class FiberWorkerLoop(object):
    
    def __init__(self):
        self.worker = []
        
    def append(self,worker):
        self.worker.append(worker)
        
    def remove(self,worker):
        self.worker.remove(worker)
        
    def __iter__(self):
        return self
    
    def __next__(self):
        for w in self.worker:
            try:
                next(w)
            except StopIteration as ex:
                # notify waining obj
                
                raise ex
            except Exception as ex:
                print(self.__class__.__name__, ex)
                raise ex
            
    def kill(self,reason=None):
        for w in self.worker:
            w.suspend()
    
    def close():
        for w in self.worker:
            w.kill("close")
        

class FiberWorker(object):
    
    def __init__(self,func,fiberloop=None,debug=True,**kwargs):
        self.debug = debug
        self.func = func
        self.fiberloop = fiberloop
        self._run = False
        self.kwargs = kwargs
        self.reset("init")
        
    def reset(self,reason="reset"):
        self.kill(reason)
        self.debug and print( "->",reason, id(self))
        self.rc = None
        self.err = None
        self._inner = self.func(self)
        
    def start(self):
        self.resume()
        
    def resume(self):
        try:
            if self._run or self.fiberloop==None:
                return
            self.fiberloop.append(self._inner)
        finally:
            self._run = True            
        
    def suspend(self):
        try:
            if not self._run or self.fiberloop==None:
                return
            self.fiberloop.remove(self._inner)
        finally:
            self._run = False            

    def __next__(self):
        try:
            self.rc = next( self._inner )
            return self.rc
        except StopIteraton as ex:
            self.suspend()
            raise ex
        except Exception as ex:
            print(ex)
            self.suspend()
            self.err = ex
            raise ex
    
    def __iter__(self):
        return self
        
    def kill(self,reason="kill"):
        self.debug and print(">",reason, id(self),)
        self.suspend()
        self._inner = None
    
    def close(self):
        self.kill("close")
 
 
def w1func(self):
    c = 0
    while True:
        c+=1
        print("w1", c, self.kwargs)
        yield 
    

fl = FiberWorkerLoop()

w1 = FiberWorker( func=w1func, fiberloop=fl, a=3 )
    
w1.start()

next(fl)
next(fl)
next(fl)

w1.suspend()

print("hop1")
next(fl)
print("hop2")
next(fl)

w1.resume()

next(fl)
next(fl)

print("reset")

w1.reset()
w1.start()

next(fl)
next(fl)


