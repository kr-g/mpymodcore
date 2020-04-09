
"""
    fiber
    https://en.wikipedia.org/wiki/Fiber_(computer_science)
    
    yield
    https://en.wikipedia.org/wiki/Cooperative_multitasking
    
    (c)2020 K. Goger (k.r.goger@gmail.com)
    
"""


import time
import math

from modcore.log import LogSupport


class FiberLoop(LogSupport):
    
    def __init__(self):
        LogSupport.__init__(self)
        self.fiber = []
        self._prep()
        
    def _prep(self):
        self.done=[]
        self.err=[]
              
    def add(self,fbr):
        self.fiber.append(fbr)
        
    def kill(self,fbr,reason=None):
        self.fiber.remove(fbr)
        fbr.kill(reason)
        
    def kill_all(self,reason=None):
        for f in self.fiber:
            f.kill(reason)
            
    def kill_expire_ms(self, timeout, reason=None):
        for f in self.fiber:
            if f.run_time_diff_ms()>=timeout:
                f.kill(reason)
        
    def status(self):
        if len(self.done)>0 or len(self.err)>0:
           return (self.done,self.err)

    def all_done(self):
        return len(self.fiber)==0
    
    def loop(self):
        try:
            next(self)
        except StopIteration:
            pass
        return len(self)>0
    
    def __next__(self):
        self._prep()
        for f in self.fiber:
            try:
                r = next(f)
                # throw away r, and continue with next fiber
            except StopIteration as ex:
                # this one is finished, remove it
                self.fiber.remove(f)
                self.done.append(f)
            except Exception as ex:
                self.fiber.remove(f)
                self.err.append(f)
                self.excep(ex, "fiber failed" )
        if self.all_done():
            raise StopIteration
        return self.status()
        
    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self.fiber)
            

class Fiber(LogSupport):
    
    def __init__(self,func):
        LogSupport.__init__(self)
        # save the generator object
        self.func = func
        if self.func.__class__.__name__!="generator":
            raise Exception("no generator provided, got", type(self.func) )
        
        self.start_time = time.ticks_ms()
        self.stop_time = 0
        self.rc = None
        self.err = None
        
        # some more housekeeping
        self.cpu_time = 0
        self.lastcall_start = 0
        self.lastcall_time = 0
        
        # trace performance younter accordigly to the log level
        ## todo
        # change later to debug
        self._perf_counter = self.info()
        
    def run_time(self):
        return time.ticks_diff(self.stop_time,self.start_time)

    def run_time_diff_ms(self):
        now = time.ticks_ms()
        return time.ticks_diff(now,self.start_time)
    
    def kill(self,reason=None):
        self.func = None
        self.__kill__(reason)
        
    def __kill__(self,reason=None):
        pass

    def __next__(self):
        try:
            if self._perf_counter:
                self.lastcall_start = time.ticks_ms()
            
            self.rc = next(self.func)
            
            if self._perf_counter:
                now = time.ticks_ms()
                self.lastcall_time = time.ticks_diff(now,self.lastcall_start)
                self.cpu_time += self.lastcall_time
            
            return self.rc
        except StopIteration as ex:
            # here we are done
            raise ex
        except Exception as ex:
            self.err = ex
            self.excep(ex)
            raise ex
        finally:
            self.stop_time = time.ticks_ms()
      
    def __iter__(self):
        return self
    
    def __repr__(self):
        return self.__class__.__name__ \
                + "(start: " + str(self.start_time) \
                +", stop: " + str(self.stop_time) \
                + ", run time: " + str(self.run_time()) \
                + ", rc: " + str(self.rc) \
                + ", cpu time: " + str( self.cpu_time ) \
                + ("" if self.err==None else repr(err) ) \
                + ")"


class FiberTimeoutException(Exception):
    pass

class FiberWatchdog(Fiber):
    
    # default timeout is math.e
    # first i wanted to use math.pi,
    # but i fear the math.tau discussion
    def __init__(self,func,max_time_auto_kill_ms=1000*math.e):
        Fiber.__init__(self,func)
        self.max_time_auto_kill_ms = max_time_auto_kill_ms

    def __next__(self):
        if self.run_time_diff_ms() >= self.max_time_auto_kill_ms:
            raise FiberTimeoutException()
        return super().__next__()
        
            
            

def sample(path):
    
    #fibers only accept generator functions, so a yield is required
    def _print_final_message(a):
        print(a)
        # return code for fbr.rc
        yield 153

    # the generator function for the fiber
    # since at the end a new fiber is scheduled it is
    # required to pass here the fiberloop too
    # in general this is not required
    def _send_chunk(buffer_size,name,floop):
        with open(path) as f:
            while True:
                
                # the basic idea                
                #
                # do a portion of work, and yield
                #
                # important:
                # _never_ use time.sleep() or long blocking func within a fiber
                # since this will block all others from processing
                #
                c = f.read(buffer_size)
                c = c.replace("\r",".")
                c = c.replace("\n",".")
                print(name,c)
                if len(c)==0:
                    break                
                # with yield code control is handed over to the next fiber
                yield
        # this is just sort of sugar, and not needed in general...
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ) ) )   


    fl = FiberLoop()

    # first fiber is canceled after 500ms because it 
    fl.add( FiberWatchdog(_send_chunk(10,"eins", fl), max_time_auto_kill_ms=500 )) 
    fl.add( Fiber(_send_chunk(15,"zwei", fl) )) 
    fl.add( Fiber(_send_chunk(150,"drei", fl) )) 

    for status_change in fl:
        if status_change:
            print(status_change)
            
    last_status = fl.status()
    print(last_status)
    
    # try
    # from modcore.fiber import sample
    # sample("boot.py")
    
    