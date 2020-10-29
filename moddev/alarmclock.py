"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time

from modcore import modc, Module, LifeCycle

from .ntp import ntp_serv
from .eventemitter import EventEmitter


def _time():
    return ntp_serv.time()


def _utc():
    return ntp_serv.utctime()


ONE_DAY_SEC = 60 * 60 * 24

# this alarm rings every day
class AlarmClock(EventEmitter):
    def watching_events(self):
        return [
            "ntp",
        ]

    def init(self):
        super().init()
        self.conf_alarm_time = None
        self.is_utc = False
        self.alarm_time = None

        # self.check_lifecycle = False ##todo ?

    def conf(self, config=None):
        if config != None:

            # important. call config of EventEmitter
            super().conf(config)

            self.conf_alarm_time = config.get(self.id, None)  ##todo None?
            self.info("alarm time", self.conf_alarm_time)

            utc = config.get(self.id + ":utc", "False")
            self.is_utc = str(utc).lower() == "true"

        if self.conf_alarm_time == None:
            self.warn("no alarm configured")

    def start(self):
        self.recalc()

    def __loop2__(self, config=None, event=None, data=None):

        if event == None:
            return

        if event == "ntp":
            val = self.event_data_value(data)
            if val == True:
                self.info("received", event, val)
                self.recalc()
            return False

    def __emit__(self, config=None):

        if self.alarm_time == None:
            return

        now = self.time()

        if now >= self.alarm_time:
            self.info("alarm, reschedule next alarm")
            self.info(
                "current",
                list(time.localtime(now)),
                list(time.localtime(self.alarm_time)),
            )
            # set next alarm to tomorrow
            self.recalc(ONE_DAY_SEC)
            return self.__alarm__(config=config) or True

    def recalc(self, offset=0):
        self.info("recalc", offset)
        self.alarm_time = None
        if self.conf_alarm_time == None:
            self.warn("no alarm configured")
            return
        try:
            h, m = self.conf_alarm_time.split(":")
            h = int(h)
            m = int(m)
            now_s = self.time()
            now = time.localtime(now_s)
            if now[3] > h or (now[3] == h and now[4] >= m):
                offset = ONE_DAY_SEC
            at = list(time.localtime(now_s + offset))
            at[3] = h
            at[4] = m

            for i in range(5, len(at)):
                at[i] = 0

            self.info("recalc alarm", at)
            self.alarm_time = time.mktime(at)

        except Exception as ex:
            self.excep(ex, "alarm time mismatch", self.conf_alarm_time)

    def time(self):
        return _utc() if self.is_utc else _time()

    # overload this
    def __alarm__(self, config=None):
        pass
