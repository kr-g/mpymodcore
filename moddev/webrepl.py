"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import uos

from modcore import modc, Module, LifeCycle

WEBREPL_CFG = "webrepl_cfg.py"


class WebRepl(Module):
    def start(self):
        self.webrepl_start()

    def loop(self, config=None, event=None):
        pass

    def stop(self):
        self.webrepl_stop()

    # deprecated

    def webrepl_config(self, passwd):
        """set webrepl password for automatic connection during startup"""
        try:
            uos.remove(WEBREPL_CFG)
        except:
            pass
        if passwd == None:
            return
        if len(passwd) < 6:
            raise Exception("password too short")
        with open(WEBREPL_CFG, "w") as f:
            f.write("PASS = '%s'\n" % passwd)

    def webrepl_remove(self):
        """remove webrepl info and disable automatic connection during startup"""
        self.webrepl_stop()
        self.webrepl_config(None)

    def webrepl_start(self, active=True):
        """start webrepl if configured before, otherwise do nothing"""
        self.webrepl = None
        try:
            if active:
                with open(WEBREPL_CFG) as f:
                    import webrepl

                    webrepl.start()
                    self.webrepl = webrepl
            else:
                import webrepl

                webrepl.stop()
            self.info("webrepl set active=", active)
        except Exception as ex:
            self.excep(ex, "start")

    def webrepl_stop(self):
        """disabled webrepl, no reconfiguration of prior configuration"""
        self.webrepl_start(False)


webrepl_serv = WebRepl("webrepl")
modc.add(webrepl_serv)
