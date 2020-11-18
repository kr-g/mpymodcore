from modcore import modc, LifeCycle
from modext.misc.async_mod import asyncio, AsyncModule, AsyncSkeletonModule
from modext.auto_config.ext_spec import Plugin


mod_async_sample = AsyncSkeletonModule()


async def the_sample_code(self):
    try:
        while True:
            if self.stop_sig.is_set():
                break
            await asyncio.sleep(5)
            self.info("sample async routine running")
    except Exception as ex:
        self.excep(ex, "sample async routine")
    self.info("async routine stopping")


@mod_async_sample.hook(LifeCycle.LOOP, before=True)
def before_loop_run(self):
    self.info("before loop hook called")
    # important !!!
    self.create_task(the_sample_code)
    self.info("sample async task created", self.atask)


@mod_async_sample.hook(LifeCycle.LOOP, after=True)
def after_loop_run(self):
    self.info("after loop hook called")
    self.cancel_task()
    self.info("sample async task prepared cancelation")


modc.add(mod_async_sample)


# this does nothing since the sample do not provide custom generators for WindUp
class SampleAsync_plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "sample asyncio module"
        ## todo remove
        self.path_spec = "mod3rd.skeleton"
        # self.generators = []
        # self.url_caption_tuple_list = []


app_ext = [SampleAsync_plugin()]
