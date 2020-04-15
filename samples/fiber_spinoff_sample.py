
from modcore.fiber import *

"""

this deals with a more complex scenario, where an object is moved out
of, and moved an other context; but staying in the same fiber loop

## todo, describe use cases more in detail

"""

def sample(path,sample_no=0,debug=True,prt=True,timer=True,blksize=64):
    
    #fibers only accept generator functions, so a yield is required
    def _print_final_message(a):
        prt and print(a)
        # return code for fbr.rc
        yield 153
        
    def _send_chunk_file(buffer_size,name,f,floop):
        
        # do a portion of work, and yield
        
        while True:
            c = f.read(buffer_size)
            if len(c)==0:
                break                
            c = c.replace("\r",".")
            c = c.replace("\n",".")
            prt and print(name,c)
            # yield code control 
            yield
        
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ), timer=timer ) )
        
    def _send_chunk(buffer_size,name,fbrctx,floop):
        prt and print("fbrctx",fbrctx)
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
                if len(c)==0:
                    break                
                c = c.replace("\r",".")
                c = c.replace("\n",".")
                prt and print(name,c)                
                # with yield code control 
                yield
        
        floop.add( Fiber( _print_final_message("\n***done "+ name +"\n" ), timer=timer ) )   


    fl = FiberLoop(timer=timer)

    #
    # use directly as context manager
    
    if sample_no==0:   
        with FiberContext(open(path),debug=debug) as fbrctx:
            prt and print("fbrctx",fbrctx)
            # if the guard is not move out right here it will be closed
            fl.add( Fiber( _send_chunk(blksize,"eins", fbrctx.spin_off(), fl ), timer=timer ) )

    #
    # or ... hand it over and do the with block in the fiber function
    
    if sample_no==1:   
        fbrctx = FiberContext(open(path),debug=debug)
        prt and print("fbrctx",fbrctx)
        fl.add( Fiber( _send_chunk(blksize,"zwei", fbrctx, fl ), timer=timer ) )        

    #
    # or ... let the fiber itself do spin_off, and close 
    # and have a more simple fiber func notation
    # this will work good in scenarios where the guard is not handed
    # further downwards
    
    if sample_no==2:   
        fbrctx = FiberContext(open(path),debug=debug)
        prt and print("fbrctx",fbrctx)
        f = fbrctx()
        fl.add( Fiber( _send_chunk_file(blksize,"drei", f, fl ), ctx=fbrctx, timer=timer ) )
    
    # the fiber loop

    sta = time.ticks_ms()

    for status_change in fl:
        if status_change:
            print(status_change)
            
    sto = time.ticks_ms()
    
    last_status = fl.status()
    print(last_status)    
    
    # print the summary
    print()
    print(fl)
    
    print( time.ticks_diff( sto, sta ) )

    # try
    # from modcore.fiber import sample
    # check above for additional parameters
    # e.g.
    # sample("boot.py",sample_no)  # sample_no = 0..2

