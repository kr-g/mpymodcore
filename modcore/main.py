
from modcore import modc, Module, LifeCycle
from modcore import DEBUG, INFO, NOTSET, logger

from moddev.control import control_serv


debug_mode = True

def loop( cfg, add_loop ):    

    # turn debug level on for more detailed log info
    #modc.change_log_level( DEBUG if debug_mode else None )

    while True:

        try:
            # modules
            modc.run_loop( cfg )
            
            if control_serv.breaksignal==True:
                logger.warn("soft break")
                raise KeyboardInterrupt("break signal")
            
            # other loop eg webserv
            add_loop()
            
        except KeyboardInterrupt:
            logger.info( "\ncntrl+c, auto shutdown=", not debug_mode)
            if not debug_mode:
                modc.shutdown()                
            if not debug_mode:
                logger.info("call first")
                logger.info("modc.startup(config=cfg)")
            logger.info( "call loop() to continue" )
            break
        except Exception as ex:
            logger.excep( ex )

