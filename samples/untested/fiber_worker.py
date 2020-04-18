
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
                #raise ex
            
    def kill(self,reason=None):
        for w in self.worker:
            w.kill()
    
    def close():
        for w in self.worker:
            w.kill("close")
        

class FiberWorker(object):
    
    def __init__(self,func,workerloop=None,debug=True,**kwargs):
        self.debug = debug
        self.func = func
        self.floop = workerloop
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
            if self._run or self.floop==None:
                return
            self.floop.append(self._inner)
        finally:
            self._run = True            
        
    def suspend(self):
        try:
            if not self._run or self.floop==None:
                return
            self.floop.remove(self._inner)
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
 
   
   
def sample():

    def w1func(self):
        c = 0
        while True:
            c+=1
            if c>10:
                break
            print("w1", c, self.kwargs)
            yield 
       
    def w2func(self):
        c = 1
        while True:
            print("w2", c, self.kwargs)
            c+=c
            yield 

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


