try:
    import uasyncio as asyncio

    print("using micropython asyncio")
except:
    import asyncio

from .main import modc, loop_core, conv_to_list, debug_mode, logger, control_serv
from modcore.cntrl import get_ha_g, reset_ha_g


async_loop_tout = 1

keyboard_c = asyncio.Event()


async def endless_loop(func, tout=None):
    if tout == None:
        tout = async_loop_tout
    while True:
        try:
            func()

            if keyboard_c.is_set():
                logger.warn("keyboard_c")
                raise KeyboardInterrupt()

            if control_serv.breaksignal == True:
                logger.warn("soft break")
                raise KeyboardInterrupt()

            await asyncio.sleep_ms(tout)

        except KeyboardInterrupt:
            keyboard_c.set()
            try:
                logger.warn("stop endless_loop", func.__name__)
            except:
                logger.warn("stop endless_loop")
            break


async def loop(cfg, add_loop=None, ha_mode=False):
    def _call_func():
        loop_core(cfg, add_loop=add_loop, ha_mode=ha_mode)

    await endless_loop(_call_func)


def run_loop(cfg, add_loop=None, ha_mode=False, reset_asyncio=True):

    reset_ha_g()

    global keyboard_c
    keyboard_c.clear()
    global control_serv
    control_serv.breaksignal = False

    if reset_asyncio == True:
        # reset state
        asyncio.new_event_loop()

    if add_loop:
        add_loop = conv_to_list(add_loop)
        for aloop in add_loop:
            task = asyncio.create_task(endless_loop(aloop))
            logger.info("created async task for", aloop.__name__)

    modc.run_loop_hooks(before=True)

    try:
        # ignores ha_mode setting, just for compatibilty
        logger.info("running async loop")
        asyncio.run(loop(cfg, ha_mode=True))
    except KeyboardInterrupt as ex:
        logger.warn("cntrl+c")
        # signal to stop others
        keyboard_c.set()
        logger.info("\ncntrl+c, auto shutdown=", not debug_mode)
    except Exception as ex:
        logger.excep(ex)

    modc.run_loop_hooks(before=False)

    if not debug_mode:
        modc.shutdown()
    if not debug_mode:
        logger.info("call first")
        logger.info("modc.startup(config=cfg)")
    logger.info("call loop() to continue")
