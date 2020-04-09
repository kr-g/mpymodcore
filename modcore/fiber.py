
"""
    fiber
    https://en.wikipedia.org/wiki/Fiber_(computer_science)
    
    yield
    https://en.wikipedia.org/wiki/Cooperative_multitasking
    
"""


import time

class FiberLoop(object):
    
    def __init__(self):
        self.fiber = []
        self._prep()
        
    def _prep(self):
        self.done=[]
        self.err=[]
        
        
    def add(self,fbr):
        self.fiber.append(fbr)
        
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
        if self.all_done():
            raise StopIteration
        return self.status()
        
    def status(self):
        if len(self.done)>0 or len(self.err)>0:
           return (self.done,self.err)

    def all_done(self):
        return len(self.fiber)==0

    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self.fiber)
    
    def loop(self):
        try:
            next(self)
        except StopIteration:
            pass
        return len(self)>0
        

class Fiber(object):
    
    def __init__(self,func):
        # save the generator object
        self.func = func
        if self.func.__class__.__name__!="generator":
            raise Exception("no generator provided, got", type(self.func) )
        
        self.stop = 0
        self.start = time.ticks_ms()
        self.rc = None
        self.err = None

    def __next__(self):
        try:
            self.rc = next(self.func)
            return self.rc
        except StopIteration as ex:
            # here we are done
            raise ex
        except Exception as ex:
            self.err = ex
            raise ex
        finally:
            self.stop = time.ticks_ms()
      
    def __iter__(self):
        return self
    
    def __repr__(self):
        return "start: " + str(self.start) \
               +", stop: " + str(self.stop) \
               + ", " + str(self.run_time()) \
               + " rc: " + str(self.rc) \
               + "" if self.err==None else repr(err)

    def run_time(self):
        return time.ticks_diff(self.stop,self.start)



def sample(path):
    
    #fibers only accept generator functions, so an yield is required
    def _print_final_message(a):
        print(a)
        yield 153

    # the generator function for the fiber
    def _send_chunk(buffer_size,name,flp):
        with open(path) as f:
            while True:
                c = f.read(buffer_size)
                c = c.replace("\r",".")
                c = c.replace("\n",".")
                print(name,c)
                if len(c)==0:
                    break
                # with yield code control is handed back
                yield
        # this is just sort of sugar, and not needed...
        flp.add( Fiber( _print_final_message("\n***done "+ name +"\n" ) ) )   


    fl = FiberLoop()

    fl.add( Fiber(_send_chunk(10,"eins", fl) )) 
    fl.add( Fiber(_send_chunk(15,"zwei", fl) )) 
    fl.add( Fiber(_send_chunk(150,"drei", fl) )) 

    for status_change in fl:
        if status_change:
            print(status_change)

    # try
    # from modcore.fiber import sample
    # sample("boot.py")
    
    