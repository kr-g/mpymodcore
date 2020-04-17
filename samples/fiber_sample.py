
from modext.fiber import *


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
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ), timer=True ) )   


    fl = FiberLoop(timer=True)

    # first fiber is canceled after 500ms because it 
    fl.add( FiberWatchdog(_send_chunk(10,"eins", fl), timer=True, max_time_auto_kill_ms=500 )) 
    fl.add( Fiber(_send_chunk(15,"zwei", fl), timer=True) )
    fl.add( Fiber(_send_chunk(150,"drei", fl), timer=True ) ) 

    for status_change in fl:
        if status_change:
            print(status_change)
            
    last_status = fl.status()
    print(last_status)

    print(fl)
    
    
    # try
    # from modcore.fiber import sample
    # e.g.
    # sample("boot.py")
    
    