
import time

class FiberLoop(object):
    
    def __init__(self):
        self.fiber = []
        
    def add(self,fbr):
        self.fiber.append(fbr)
        
    def __next__(self):
        for f in self.fiber:
            try:
                r = next(f)
                # throw away r, and continue with next fiber
            except StopIteration as ex:
                # this one is finished, remove it
                self.fiber.remove(f)                
            except Exception as ex:
                self.fiber.remove(f) 
                print("ouch", ex )                
        if len(self.fiber)==0:
            raise StopIteration
            
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

    def __next__(self):
        try:
            r = next(self.func)
            return r
        except StopIteration as ex:
            # here we are done
            raise ex
        except Exception as ex:
            print("ouch", ex )
            raise ex
        finally:
            self.stop = time.ticks_ms()
      
    def __iter__(self):
        return self
    
    def __repr__(self):
        return "start: " + str(self.start) \
               +", stop: " + str(self.stop) \
               + ", " + str(self.run_time())

    def run_time(self):
        return time.diff(self.stop,self.start)



def sample():
    
    path = __file__

    #fibers only accept generator functions, so an yield is required
    def _print_final_message(a):
        print(a)
        yield

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

    while fl.loop():
        pass
    
    