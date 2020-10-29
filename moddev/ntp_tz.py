import time

from modcore import modc, Module, LifeCycle
from modcore.log import LogSupport

from .ntp import ntp_serv, NTP_EVENT, NTP_SYNC
from .timeout import Timeout


class NTP_TZ(Module):
    def watching_events(self):
        return [
            NTP_EVENT,
        ]

    def on_add(self):
        self.expires = None
        self.tz_handler_cls = None

    def init(self):
        pass

    def conf(self, config=None):
        pass

    def loop(self, config=None, event=None):
        if self.current_level() != LifeCycle.RUNNING:
            return

        if self.expires != None:
            if self.expires.elapsed():
                self.info("tz change, reload time")
                self.fire_event(NTP_SYNC)
                self.expires = None

        if event == None:
            return

        if self.is_event(event, NTP_EVENT):
            if self.tz_handler_cls == None:
                return
            handler = self.tz_handler_cls()

            duration = handler.expires()

            if duration != None:
                self.expires = Timeout(timeout=duration)
                self.info(
                    "tz expires", duration, time.localtime(time.time() + duration)
                )
            else:
                self.expires = None

    def set_tz_handler(self, hndl_cls=None):
        self.info("setting tz handler", hndl_cls)
        self.tz_handler_cls = hndl_cls
        self._set_tz_handler()

    def _set_tz_handler(self):
        ntp_serv.tz_handler_cls = self.tz_handler_cls


ntp_tz_serv = NTP_TZ()
modc.add(ntp_tz_serv)
