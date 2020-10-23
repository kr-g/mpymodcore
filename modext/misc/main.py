
from modcore import modc, Module, LifeCycle
from modcore import DEBUG, INFO, NOTSET, logger

from moddev.control import control_serv


debug_mode = True

def conv_to_list(el):
    if el!=None:
        if type(el)!=list:
            el=[el]
    return el


def loop( cfg, add_loop=None, ha_mode=False ):    

    # turn debug level on for more detailed log info
    #modc.change_log_level( DEBUG if debug_mode else None )

    global control_serv
    control_serv.breaksignal = False

    while True:
        try:
            loop_core( cfg, add_loop=add_loop, ha_mode=ha_mode )
        except KeyboardInterrupt:
            break

_modg = None

def loop_core( cfg, add_loop=None, ha_mode=False ):

    global _modg
    if ha_mode==True and _modg==None:
        _modg = modc.run_loop_g(cfg)

    add_loop=conv_to_list(add_loop)

    try:
        # modules
        if ha_mode==False:
            modc.run_loop( cfg )
        else:
            rc = next(_modg)
        
        if control_serv.breaksignal==True:
            logger.warn("soft break")
            raise KeyboardInterrupt("break signal")
        
        if add_loop != None:
            # other loop eg webserv
            for aloop in add_loop:
                aloop()
        
    except KeyboardInterrupt:
        logger.info( "\ncntrl+c, auto shutdown=", not debug_mode)
        if not debug_mode:
            modc.shutdown()                
        if not debug_mode:
            logger.info("call first")
            logger.info("modc.startup(config=cfg)")
        logger.info( "call loop() to continue" )
        raise
    except Exception as ex:
        logger.excep( ex )

