"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

_LIFECYCLE = [
    "NEW",
    "CONFIG",
    "MOUNT",
    "START",
    "RUNNING",
    "STOP",
    "UMOUNT",
    "EJECT",
    "__END",
    "__ERROR",
]


class HookSupport(object):
    def __init__(self):
        self._hooks = []

    def hook(self, lifecycle, before=False, after=False):
        def _wrapper(func):
            def _func(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            self._hooks.append((lifecycle, before, after, _func))
            return _func

        return _wrapper

    def call_hooks(self, lifecycle, before_call=True):
        for lc, b, a, func in self._hooks:
            if lc == lifecycle:
                if (before_call and b) or (before_call == False and a):
                    try:
                        func(self)
                    except Exception as ex:
                        self.excep(ex, "before_call", before_call)
                    continue


class LifeCycle(HookSupport):

    NEW = 0
    CONFIG = 1
    MOUNT = 2
    START = 3
    RUNNING = 4
    LOOP = 4
    STOP = 5
    UMOUNT = 6
    EJECT = 7
    __END = -1
    __ERROR = -2

    def __init__(self):
        HookSupport.__init__(self)
        self._lc_level = LifeCycle.__END

    # dont call the low level api directly
    # use the high level api given below
    # e.g. to umonut a module call:
    #
    # the_mod.change_level(LifeCycle.UMOUNT)
    #

    def on_add(self):
        pass

    def init(self):
        pass

    def conf(self, config=None):
        pass

    def mount(self):
        pass

    def start(self):
        pass

    #    def loop(self,config=None,event=None):
    #        pass

    def stop(self):
        pass

    def umount(self):
        pass

    def eject(self):
        pass

    def on_remove(self):
        pass

    # housekeeping

    def _get_state_tasks(self):
        state_tasks = [
            (LifeCycle.NEW, self.init, [LifeCycle.EJECT]),
            (LifeCycle.CONFIG, self.conf, [LifeCycle.EJECT]),
            (LifeCycle.MOUNT, self.mount, [LifeCycle.UMOUNT]),
            (LifeCycle.START, self.start, [LifeCycle.STOP]),
            (LifeCycle.RUNNING, None, []),
            (LifeCycle.STOP, self.stop, [LifeCycle.START]),
            (
                LifeCycle.UMOUNT,
                self.umount,
                [
                    LifeCycle.MOUNT,
                ],
            ),
            (LifeCycle.EJECT, self.eject, [LifeCycle.CONFIG]),
            (LifeCycle.__END, None, [LifeCycle.NEW]),
        ]
        return state_tasks

    def _call_level(self, m, l, config=None):
        l_func = m[1]
        curlevel = m[0]
        if l_func != None:
            if curlevel != l:
                raise Exception("internal error")

            self.call_hooks(curlevel, before_call=True)

            if curlevel == LifeCycle.CONFIG:
                l_func(config=config)
            else:
                l_func()

            self.call_hooks(curlevel, before_call=False)

        self.info("exe level", curlevel, _LIFECYCLE[curlevel])
        self._lc_level = curlevel

    # high level api

    def change_level(self, new_level, config=None):
        if self._lc_level == new_level:
            return
        st = self._get_state_tasks()
        if new_level in st[self._lc_level][2]:
            self._call_level(st[new_level], new_level, config)
        else:
            if self._lc_level < new_level:
                for l in range(self._lc_level + 1, new_level + 1):
                    m = st[l]
                    self._call_level(m, l, config)
            else:
                raise Exception(
                    "wrong level", new_level, "src", self.id, "current", self._lc_level
                )

        if new_level == LifeCycle.EJECT:
            self._lc_level = LifeCycle.__END

    def current_level(self):
        return self._lc_level

    def current_level_str(self):
        return _LIFECYCLE[self._lc_level]

    def reconfigure(self, config=None):
        if self._lc_level < LifeCycle.CONFIG:
            raise Exception("level too low; config first")
        cur_level = self._lc_level
        self.change_level(LifeCycle.EJECT)
        self.change_level(LifeCycle.CONFIG, config)
        self.change_level(cur_level, config)

    def shutdown(self):
        if self._lc_level < LifeCycle.CONFIG:
            return
        self.change_level(LifeCycle.EJECT)

    def startup(self, config=None):
        self.change_level(LifeCycle.RUNNING, config)
