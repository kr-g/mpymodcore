
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

# faking the platform, requires py 3.7

import time as _time

class time(object):
    @staticmethod
    def time():
        return _time.time()
    @staticmethod
    def ticks_ms():
        # py 3.7
        return _time.time_ns()/1000000
    @staticmethod
    def ticks_diff(t1,t2):
        return t1-t2
    @staticmethod
    def ticks_add(t1,t2):
        return t1+t2
    @staticmethod
    def sleep_ms(t):
        return _time.sleep(t/1000)
    
class LogSupport(object):
    
    def info(self,*args):
        print(*args)
    def excep(self,*args):
        print(*args)

# end of platform fake

# doubled code, testrecorder tid and ...

__ids = {}
__id_cnt = 0

def tid(obj):
    global __ids
    global __id_cnt 
    oid = id(obj)
    rid = None
    if oid in __ids:
        rid = __ids[oid]
    else:
        __id_cnt += 1
        rid = __id_cnt
        __ids[oid]=__id_cnt
    return "{tid:"+str(rid)+"}"

class TimerSupport(object):
    
    def __init__(self):
        self.start_timer()
        
    def start_timer(self):
        self.start_time = time.ticks_ms()
        self.stop_time = 0       
        self.cpu_time = 0
        self.lastcall_start = 0
        self.lastcall_time = 0
    
    def run_time(self):
        return time.ticks_diff(self.stop_time,self.start_time)

    def run_time_diff_ms(self):
        now = time.ticks_ms()
        return time.ticks_diff(now,self.start_time)

    def stop_timer(self):
        self.stop_time = time.ticks_ms()
        
    def measure_timer(self,start=True):
        if start:
            self.lastcall_start = time.ticks_ms()
        else:
            now = time.ticks_ms()
            self.lastcall_time = time.ticks_diff(now,self.lastcall_start)
            self.cpu_time += self.lastcall_time
    
    def __repr__(self):
        return self.__class__.__name__ \
                + "(start: " + str(self.start_time) \
                +", stop: " + str(self.stop_time) \
                + ", run time: " + str(self.run_time()) \
                + ", cpu time: " + str( self.cpu_time ) \
                + ")"

# end of doubled code

#from testrecorder import TestRecorder, tid


class FiberWorkerLoop(TimerSupport):
    
    def __init__(self, react_time_ms=None, debug=True, timer=True ):
        TimerSupport.__init__(self)
        self.debug = debug
        self.timer = timer
        self.worker = []
        self.react_time = react_time_ms/1000 if react_time_ms!=None else None
        
    def append(self, worker ):
        self.worker.append(worker)
        
    def remove(self, worker ):
        self.worker.remove(worker)
        
    def kill(self, reason="kill" ):
        for w in self.worker:
            w.kill(reason)
    
    def close(self):
        for w in self.worker:
            w.kill("close")
        
    def _schedule(self,react_time=None,max=None):
        react_time = self.react_time if react_time==None else react_time
        try:
            time_p_fbr = react_time / ( len(self) if max==None else max )
            return time_p_fbr * 1000
        except:
            # division by zero
            return None
        
    def __len__(self):
        return len(self.worker)
    
    def __iter__(self):
        return self
    
    def __next__(self):
                
        tpf = self._schedule()
        ## todo measure_timer ?
        self.timer and self.start_timer()
        for w in self.worker:
            
            w._switch_time = time.ticks_add( tpf, time.ticks_ms() ) if tpf!=None else None
            
            try:
                next(w)
                
            except StopIteration as ex:
                self.debug and print( self.__class__.__name__, ex.__class__.__name__, tid(w), ex )                
                pass

            except Exception as ex:
                self.debug and print( self.__class__.__name__, ex.__class__.__name__, tid(w), ex )
                pass
        self.timer and self.stop_timer()
            

class FiberWaitTimeout(Exception):
    pass

class FiberWorker(object):
    
    def __init__(self, func=None, workerloop=None, parent=None, debug=True, **kwargs ):
        self.debug = debug
        self.func = func 
        self.floop = workerloop
        self.parent = parent
        self._run = False
        self.kwargs = kwargs
        self._switch_time = None
        self.reset("init")
        
    def reset(self, reason="reset" ):
        self.kill(reason)
        self.debug and print( self.__class__.__name__, "reset", reason, tid(self),)
        self.rc = None
        self.err = None
        self.done = None
        self._inner = self.__fiber__()
        self.init()
        
    def __fiber__(self):
        if self.func==None:
            raise Exception("no fiber defined, or __fiber__ overloaded")
        return self.func(self)
    
    def init(self):
        pass
        
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

    def sleep_ms(self,msec=None):
        if msec==None or msec==0:
            yield
            return
        now = time.ticks_ms()
        stop = time.ticks_add( now, msec )
        while True:
            if time.ticks_diff( stop, time.ticks_ms() )<0:
                break
            yield

    def switch(self):
        if self._switch_time==None:
            return 
        if time.ticks_diff( self._switch_time, time.ticks_ms() )>0:
            return False
        self.debug and print( self.__class__.__name__, "switch", tid(self),)
        yield
        return True

    def waitfor_ms(self,worker,timeout_ms=-1):
        if worker==None:
            return
        now = time.ticks_ms()
        stop = time.ticks_add( now, timeout_ms )
        while True:
            if worker.done!=None:
                return worker.done,worker.rc,worker.err
            if time.ticks_diff( stop, time.ticks_ms() )<0:
                return worker.done,None,None
                #raise FiberWaitTimeout()
            yield          
        
    def spawn_fiber(self, worker):
        self.suspend("spawn")
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
            self.done = time.ticks_ms()
            self._done_revoke_parent()
            raise ex
        except Exception as ex:
            self.debug and print( self.__class__.__name__, "except", tid(self), ex)
            self.err = ex
            self.done = time.ticks_ms()
            self._done_revoke_parent("exception")
            raise ex
    
    def __iter__(self):
        return self
        
    
def sample():

#    with TestRecorder("fiber-worker-sample",record=False,nil=True,\
#                      dest_dir = "./") as tr:

        # a fiber class 
        class w1func(FiberWorker):

            def init( self ):
                print("args", self.kwargs )

            def __fiber__(self):
                c = 0
                while True:
                    c+=1
                    if c>100:
                        break
                    print("w1", c, self.kwargs, tid(self) )
                    yield 
        
        # a fiber function
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
            
            print("sleep", time.time(), self._switch_time)
            
            # block this fiber !!!
            time.sleep_ms(300) # decrease this to see switch control below
            
            print("wake")
            
            # this switches to another fiber depending of time consumed so far
            sw = yield from self.switch()
            print( "switched", sw )
                  
            self.soft_sleep = 0
            c = 1
            stat = None
            while True:
                print("w2", c, self.kwargs, tid(self))
                c+=c
                
                print("sleeping softly")
                yield from self.sleep_ms(100)
                self.soft_sleep += 1
                print("smooth wake up",self.soft_sleep)
                
                # wait for w1 with timeout 250 ms
                if self.soft_sleep>5 and stat==None:
                    print( "waiting for w1 to end")
                    stat,rc,err = yield from self.waitfor_ms( self.wait_var_w1, 250 )
                    print( "w1 waiting result", stat,rc, err )
                    
                #yield 


        global fl
        fl = FiberWorkerLoop(react_time_ms=250)

        # fiber class and function usage
        w1 = w1func( workerloop=fl, a=5, b=6 )
        w2 = FiberWorker( func=w2func, workerloop=fl, a=15, c=7 )
        
        w2.wait_var_w1 = w1
            
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
        
        # this is not really recommendet
        # checking inner state of w2, and stop after 12 iterations
        while w2.done == None and w2.soft_sleep<12:
            next(fl)
        
        #print(fl)


sample()

