
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


class FiberLoop(LogSupport,TimerSupport):
    
    def __init__(self):
        LogSupport.__init__(self)
        TimerSupport.__init__(self)
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
        self.measure_timer()
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
        self.measure_timer(False)
        if self.all_done():
            self.stop_timer()
            raise StopIteration
        return self.status()
        
    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self.fiber)
 
        
class Fiber(LogSupport,TimerSupport):
    
    def __init__(self,func,ctx=None):
        LogSupport.__init__(self)
        TimerSupport.__init__(self)
        # save the generator object
        self.func = func
        self.ctx = None if ctx == None else ctx.spin_off()
        if self.func.__class__.__name__!="generator":
            raise Exception("no generator provided, got", type(self.func) )

        self.rc = None
        self.err = None

        # trace performance younter accordigly to the log level
        ## todo
        # change later to debug
        self._perf_counter = self.info()
        
    def close(self):
        if self.ctx!=None:
            self.ctx.close()
            self.ctx=None
            
    def spin_off(self):
        try:
            return self.ctx.spin_off()
        finally:
            self.ctx = None
                
    def kill(self,reason=None):
        self.close()
        self.func = None
        self.__kill__(reason)
        
    def __kill__(self,reason=None):
        pass

    def __next__(self):
        try:
            if self._perf_counter:
                self.measure_timer()
            
            self.rc = next(self.func)
            
            if self._perf_counter:
                self.measure_timer(False)
            
            return self.rc
        except StopIteration as ex:
            # here we are done
            self.close()
            raise ex
        except Exception as ex:
            self.err = ex
            self.excep(ex)
            self.close()
            raise ex
        finally:
            self.stop_timer()
      
    def __iter__(self):
        return self
    
    def __repr__(self):
        return self.__class__.__name__ \
               + "( rc: " + str(self.rc) \
                + ("," if self.err==None else repr(self.err) ) \
                + ") " \
                + TimerSupport.__repr__(self)


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


class Guard(object):
    
    def __init__(self,guard, debug=False ):
        self._guard = guard
        self.debug = debug

    def close(self):
        self.debug and print(">close",self.__class__.__name__)
        if self._guard != None:
            self.debug and print(">close-guard",self.__class__.__name__)
            self._guard.close()
            self._guard = None
        
    def __enter__(self):
        self.debug and print(">enter",self.__class__.__name__)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">exit",self.__class__.__name__)
        try:
            self.__on_exit__(exc_type, exc_value, traceback)
        finally:
            self.close()
    
    # use this to enhance your code
    def __on_exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">onexit",self.__class__.__name__)
        pass
    
    def __call__(self):
        return self._guard
    
    def __repr__(self):
        return repr(self._guard)


class Detachable(Guard):
    
    def spin_off(self):
        self.debug and print( ">detach", self.__class__.__name__ )
        try:
            return self.__class__(self._guard,self.debug)
        finally:
            self._guard = None            


class FiberContext(Detachable):
       
    # use this to enhance your code
    def __on_exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">leaving",self.__class__.__name__)
        

        

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

    print(fl)
    
    

def sample2(path,sample_no=0):
    
    #fibers only accept generator functions, so a yield is required
    def _print_final_message(a):
        print(a)
        # return code for fbr.rc
        yield 153
        
    def _send_chunk_file(buffer_size,name,f,floop):
        
        # do a portion of work, and yield
        
        while True:
            c = f.read(buffer_size)
            c = c.replace("\r",".")
            c = c.replace("\n",".")
            print(name,c)
            if len(c)==0:
                break                
            # yield code control 
            yield
        
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ) ) )
        
    def _send_chunk(buffer_size,name,fbrctx,floop):
        print("fbrctx",fbrctx)
        #
        # remember fbrctx is a context manager
        # if not used continuously in that way __exit__
        # will be not called, so spin_off here again
        # it will just copy the guard, not much overhead
        #
        with fbrctx.spin_off() as fc:
            # get the file from the context by calling the context
            f = fc()
            while True:
                
                # do a portion of work, and yield

                c = f.read(buffer_size)
                c = c.replace("\r",".")
                c = c.replace("\n",".")
                print(name,c)
                if len(c)==0:
                    break                
                # with yield code control 
                yield
        
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ) ) )   


    fl = FiberLoop()

    #
    # use directly as context manager
    
    if sample_no==0:   
        with FiberContext(open(path),debug=True) as fbrctx:
            print("fbrctx",fbrctx)
            # if the guard is not move out right here it will be closed
            fl.add( Fiber( _send_chunk(15,"eins", fbrctx.spin_off(), fl ) ) )

    #
    # or ... hand it over and do the with block in the fiber function
    
    if sample_no==1:   
        fbrctx = FiberContext(open(path),debug=True)
        print("fbrctx",fbrctx)
        fl.add( Fiber( _send_chunk(15,"zwei", fbrctx, fl ) ) )        

    #
    # or ... let the fiber itself do spin_off, and close 
    # and have a more simple fiber func notation
    # this will work good in scenarios where the guard is not handed
    # further downwards
    
    if sample_no==2:   
        fbrctx = FiberContext(open(path),debug=True)
        print("fbrctx",fbrctx)
        f = fbrctx()
        fl.add( Fiber( _send_chunk_file(15,"drei", f, fl ), ctx=fbrctx ) )
    
    # the fiber loop

    for status_change in fl:
        if status_change:
            print(status_change)
            
    last_status = fl.status()
    print(last_status)    
    
    # print the summary
    print()
    print(fl)
    
    
    # try
    # from modcore.fiber import sample, sample2
    # sample("boot.py")
    # sample2("boot.py",sample_no)  # sample_no = 0..2
    
    