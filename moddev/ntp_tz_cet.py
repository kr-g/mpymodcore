import time

from .ntp import ntp_serv, TZ_Support

# https://en.wikipedia.org/wiki/Central_European_Time
# https://en.wikipedia.org/wiki/Daylight_saving_time


class TZ_cet(TZ_Support):
    def __init__(self):

        year_tm = self._get_year_tm()

        summer = self._patch(year_tm, self._summer_start_pad())
        self.summer_tm = self._strategy(summer)
        self.summer = time.mktime(self.summer_tm)

        winter = self._patch(year_tm, self._winter_start_pad())
        self.winter_tm = self._strategy(winter)
        self.winter = time.mktime(self.winter_tm)

    def _get_year_tm(self, offs=0):
        n = self._utc_time()
        tn = time.localtime(n)
        return (tn[0] + offs, 0, 0, 0, 0, 0, 0, 0)

    def get_current_tz(self):
        n = self._utc_time()
        offset = self._utc_tz_offset()
        if n >= self.summer and n < self.winter:
            offset += self._summer_tz_offset()
        return offset

    def expires(self):
        exp = None
        cur_time = self._utc_time()
        if cur_time > self.winter:
            # next year
            year_tm = self._get_year_tm(1)
            summer = self._patch(year_tm, self._summer_start_pad())
            summer_tm = self._strategy(summer)
            self.summer = time.mktime(self.summer_tm)
        if cur_time < self.summer:
            exp = self.summer - cur_time
        if cur_time < self.winter:
            exp = self.winter - cur_time
        return exp

    def _utc_time(self):
        # return ntp_serv.utc()
        return time.time()

    def _patch(self, tm, tp):
        tm = list(tm)
        for i in range(0, 3):
            tm[i + 1] = tp[i]
        return tm

    def _strategy(self, t):
        return self._find_last_sunday(t)

    def _find_last_sunday(self, t):
        # this is official across europe
        # refer wiki article above
        tm = list(time.localtime(time.mktime(t)))
        dow = tm[6]
        if dow != 6:
            tm[2] -= dow + 1
            tm[6] = 6
        return tm

    def _summer_start_pad(self):
        # 31 march, 1am utc
        return 3, 31, 1

    def _winter_start_pad(self):
        # 31 oct, 1am utc
        return 10, 31, 1

    def _utc_tz_offset(self):
        # berlin, rome, warsaw
        return 3600

    def _summer_tz_offset(self):
        return 3600

    def __repr__(self):

        now = time.time()
        offset = self.get_current_tz()
        loctime = now + offset
        expires = self.expires()

        return {
            "now_utc": now,
            "now_utc_tm": time.localtime(now),
            "tz_offset": offset,
            "now_tz_tm": time.localtime(loctime),
            "summer": self.summer,
            "summer_tm": self.summer_tm,
            "winter": self.winter,
            "winter_tm": self.winter_tm,
            "expires": expires,
        }
